from datetime import date

from backend.models.travel import TravelRequest
from backend.services.mcp_travel_service import (
    search_flights_via_mcp,
    search_hotels_via_mcp,
)
from backend.agents.travel_agent import calculate_hotel_cost




async def plan_trip_via_mcp(
    request: TravelRequest,
) -> list[dict]:

    # --------------------------------------------------
    # 1. Search flights through MCP
    # --------------------------------------------------

    flight_response = await search_flights_via_mcp(
        origin=request.origin,
        destination=request.destination,
        departure_date=str(request.departure_date),
        cabin_class=request.cabin_class,
    )

    # --------------------------------------------------
    # 2. Search hotels through MCP
    # --------------------------------------------------

    hotel_response = await search_hotels_via_mcp(
        destination=request.destination,
        hotel_min_rating=request.hotel_min_rating,
    )

    flights = flight_response.get("result", [])
    hotels = hotel_response.get("result", [])

    print(f"Flights received from MCP: {len(flights)}")
    print(f"Hotels received from MCP: {len(hotels)}")

    # --------------------------------------------------
    # 3. Deterministic travel planning
    # --------------------------------------------------

    results = []

    for flight in flights:

        if flight["stops"] > request.max_stops:
            continue

        if flight["cabin_class"] != request.cabin_class:
            continue

        for hotel in hotels:

            if hotel["rating"] < request.hotel_min_rating:
                continue

            nights, hotel_total = calculate_hotel_cost(
                hotel["nightly_price"],
                request.departure_date,
                request.return_date,
            )

            total_cost = (
                flight["price"]
                + hotel_total
            )

            if total_cost > request.max_budget:
                continue

            results.append(
                {
                    "flight": flight,
                    "hotel": hotel,
                    "nights": nights,
                    "flight_cost": flight["price"],
                    "hotel_cost": hotel_total,
                    "total_cost": total_cost,
                    "budget": request.max_budget,
                    "remaining_budget": (
                        request.max_budget
                        - total_cost
                    ),
                }
            )

    # Cheapest first
    results.sort(
        key=lambda option: option["total_cost"]
    )

    return results