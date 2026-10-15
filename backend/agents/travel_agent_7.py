from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

from backend.models.travel import TravelRequest

from backend.agents.mcp_travel_agent import (
    plan_trip_via_mcp,
)

from rag.retriever import (
    get_knowledge_context,
)


llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Smart Travel Assistant.

You receive travel options that were retrieved
through MCP tools and filtered by deterministic
Python business logic.

Rules:

1. Never invent flights.
2. Never invent hotels.
3. Never invent prices.
4. Never change the calculated total.
5. Never recommend an option that was not provided.
6. Clearly show flight and hotel costs.
7. Clearly show the total trip cost.
8. Clearly show the remaining budget.
9. Use the travel knowledge context when explaining
   travel policies.
10. If policy information is missing, say it needs
    to be confirmed with the airline or hotel.
11. Do not claim that anything has been booked.
12. Recommend the best available option based on the
    supplied options.

Keep the answer clear and concise.
"""
        ),
        (
            "human",
            """
Travel request:

{travel_request}

Travel options retrieved through MCP:

{travel_options}

Relevant travel knowledge:

{knowledge_context}

Give the user the best recommendation and explain why.
"""
        ),
    ]
)


async def run_phase7_travel_agent(
    request: TravelRequest,
) -> str:

    # ---------------------------------------------
    # MCP + deterministic planning
    # ---------------------------------------------

    trip_options = await plan_trip_via_mcp(
        request
    )

    # ---------------------------------------------
    # RAG
    # ---------------------------------------------

    knowledge_context = get_knowledge_context(
        f"""
        Travel from {request.origin}
        to {request.destination}.

        Cabin class:
        {request.cabin_class}

        Hotel rating:
        {request.hotel_min_rating}

        Budget:
        {request.max_budget}
        """
    )

    # ---------------------------------------------
    # Prepare options for LLM
    # ---------------------------------------------

    formatted_options = []

    for option in trip_options:

        formatted_options.append(
            {
                "airline": option["flight"]["airline"],
                "flight_number": option["flight"]["flight_number"],
                "flight_price": option["flight_cost"],
                "stops": option["flight"]["stops"],
                "duration_hours": option["flight"]["duration_hours"],
                "hotel": option["hotel"]["name"],
                "hotel_rating": option["hotel"]["rating"],
                "hotel_cost": option["hotel_cost"],
                "nights": option["nights"],
                "total_cost": option["total_cost"],
                "remaining_budget": option["remaining_budget"],
            }
        )

    # ---------------------------------------------
    # Handle no results
    # ---------------------------------------------

    if not formatted_options:

        formatted_options = [
            {
                "message": (
                    "No travel options matched "
                    "the user's requirements."
                )
            }
        ]

    # ---------------------------------------------
    # Send to LLM
    # ---------------------------------------------

    messages = prompt.format_messages(
        travel_request=request.model_dump(),
        travel_options=formatted_options,
        knowledge_context=knowledge_context,
    )

    response = await llm.ainvoke(
        messages
    )

    return response.content