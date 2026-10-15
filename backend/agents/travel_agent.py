from datetime import date

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.config.settings import OPENAI_MODEL
from backend.models.travel import TravelRequest
from rag.retriever import get_knowledge_context
from backend.services.flight_service import search_flights
from backend.services.hotel_service import search_hotels


# ============================================================
# 1. OpenAI model
# ============================================================

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
)


# ============================================================
# 2. Travel request extraction prompt
# ============================================================

travel_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a travel request extraction assistant.

Extract travel requirements from the user's message.

Return only information that is explicitly provided
or can safely be inferred.

The required fields are:

- origin
- destination
- departure_date
- return_date
- passengers
- cabin_class
- max_budget
- max_stops
- hotel_min_rating

Today's date is {today}.

If an important field is missing, do not invent it.
""",
        ),
        (
            "human",
            "{user_request}",
        ),
    ]
)


# ============================================================
# 3. Convert LLM output into TravelRequest
# ============================================================

structured_llm = llm.with_structured_output(TravelRequest)

travel_extractor = travel_prompt | structured_llm


def extract_travel_request(user_request: str) -> TravelRequest:
    """
    Convert a natural-language travel request
    into a validated TravelRequest object.
    """

    today = date.today().isoformat()

    return travel_extractor.invoke(
        {
            "user_request": user_request,
            "today": today,
        }
    )


# ============================================================
# 4. RAG travel knowledge
# ============================================================

def get_travel_knowledge(user_request: str) -> str:
    """
    Retrieve relevant travel knowledge from the RAG database.
    """

    return get_knowledge_context(
        query=user_request,
        k=3,
    )


# ============================================================
# 5. Calculate hotel cost
# ============================================================

def calculate_hotel_cost(
    nightly_price: float,
    check_in: date,
    check_out: date,
) -> tuple[int, float]:

    nights = (check_out - check_in).days

    if nights <= 0:
        raise ValueError(
            "Check-out date must be after check-in date."
        )

    total = nightly_price * nights

    return nights, total


# ============================================================
# 6. Find valid flight + hotel combinations
# ============================================================

def plan_trip(request: TravelRequest) -> list[dict]:
    """
    Search mock flights and hotels and apply
    deterministic travel constraints.
    """

    flights = search_flights(request)
    hotels = search_hotels(request)

    results = []

    for flight in flights:

        # Maximum stops
        if flight.stops > request.max_stops:
            continue

        # Cabin class
        if flight.cabin_class != request.cabin_class:
            continue

        for hotel in hotels:

            # Minimum hotel rating
            if hotel.rating < request.hotel_min_rating:
                continue

            # Hotel cost
            nights, hotel_total = calculate_hotel_cost(
                hotel.nightly_price,
                request.departure_date,
                request.return_date,
            )

            # Total trip cost
            total_cost = flight.price + hotel_total

            # Maximum budget
            if total_cost > request.max_budget:
                continue

            results.append(
                {
                    "flight": flight,
                    "hotel": hotel,
                    "nights": nights,
                    "flight_cost": flight.price,
                    "hotel_cost": hotel_total,
                    "total_cost": total_cost,
                    "remaining_budget": (
                        request.max_budget - total_cost
                    ),
                }
            )

    # Cheapest options first
    results.sort(
        key=lambda option: option["total_cost"]
    )

    return results


# ============================================================
# 7. Format travel options
# ============================================================

def format_options(options: list[dict]) -> str:

    if not options:
        return (
            "No flight and hotel combination "
            "matches the requested criteria."
        )

    output = []

    for index, option in enumerate(
        options,
        start=1,
    ):

        flight = option["flight"]
        hotel = option["hotel"]

        output.append(
            f"""
OPTION {index}

Flight:
{flight.airline} {flight.flight_number}
{flight.origin} → {flight.destination}
Cabin: {flight.cabin_class}
Stops: {flight.stops}
Flight price: £{option["flight_cost"]:.2f}

Hotel:
{hotel.name}
Rating: {hotel.rating}/5
Nights: {option["nights"]}
Hotel price: £{option["hotel_cost"]:.2f}

TOTAL: £{option["total_cost"]:.2f}

Remaining budget:
£{option["remaining_budget"]:.2f}
"""
        )

    return "\n------------------------\n".join(output)


# ============================================================
# 8. Final response prompt
# ============================================================

response_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a professional travel planning assistant.

Use ONLY the provided travel options and
knowledge context.

Do not invent:

- prices
- flights
- hotels
- availability
- cancellation policies

Clearly explain the best available options.

If there are no matching options, say so.

The user has not yet authorized a booking.

Never claim that anything has been booked.
""",
        ),
        (
            "human",
            """
User request:

{user_request}

Travel knowledge:

{knowledge}

Available travel options:

{options}
""",
        ),
    ]
)


response_chain = response_prompt | llm


# ============================================================
# 9. Main travel agent
# ============================================================

def run_travel_agent(user_request: str) -> dict:
    """
    Complete travel-agent workflow:

    1. Understand the user's request
    2. Validate it using TravelRequest
    3. Retrieve relevant travel knowledge
    4. Search flights
    5. Search hotels
    6. Apply budget and travel constraints
    7. Ask the LLM to explain the results
    """

    # Step 1: Extract structured travel request
    request = extract_travel_request(
        user_request
    )

    # Step 2: Retrieve RAG knowledge
    knowledge = get_travel_knowledge(
        user_request
    )

    # Step 3: Find valid combinations
    options = plan_trip(request)

    # Step 4: Convert options into readable text
    formatted_options = format_options(
        options
    )

    # Step 5: Generate final explanation
    response = response_chain.invoke(
        {
            "user_request": user_request,
            "knowledge": knowledge,
            "options": formatted_options,
        }
    )

    return {
        "request": request,
        "knowledge": knowledge,
        "options": options,
        "response": response.content,
    }