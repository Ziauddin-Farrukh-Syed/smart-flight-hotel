from datetime import date, timedelta

from mcp.server.mcpserver import MCPServer

from backend.models.travel import TravelRequest
from backend.services.flight_service import search_flights
from backend.services.hotel_service import search_hotels


# ---------------------------------------------------------
# MCP server
# ---------------------------------------------------------

mcp = MCPServer(
    "smart-flight-hotel-agent"
)


# ---------------------------------------------------------
# Flight search tool
# ---------------------------------------------------------

@mcp.tool()
def search_flights_mcp(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str = "economy",
) -> list[dict]:
    """
    Search flight options for a route.
    """

    departure = date.fromisoformat(
        departure_date
    )

    request = TravelRequest(
        origin=origin,
        destination=destination,
        departure_date=departure,
        return_date=departure + timedelta(days=1),
        passengers=1,
        cabin_class=cabin_class,
        max_budget=999999,
        max_stops=5,
        hotel_min_rating=1,
    )

    flights = search_flights(request)

    return [
        flight.model_dump()
        for flight in flights
    ]


# ---------------------------------------------------------
# Hotel search tool
# ---------------------------------------------------------

@mcp.tool()
def search_hotels_mcp(
    destination: str,
    hotel_min_rating: float = 1.0,
) -> list[dict]:
    """
    Search hotel options for a destination.
    """

    request = TravelRequest(
        origin="Unknown",
        destination=destination,
        departure_date=date(2026, 1, 1),
        return_date=date(2026, 1, 2),
        passengers=1,
        cabin_class="economy",
        max_budget=999999,
        max_stops=5,
        hotel_min_rating=hotel_min_rating,
    )

    hotels = search_hotels(request)

    return [
        hotel.model_dump()
        for hotel in hotels
        if hotel.rating >= hotel_min_rating
    ]


# ---------------------------------------------------------
# Start MCP server
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Starting Smart Flight & Hotel MCP Server..."
    )

    print(
        "MCP endpoint: http://127.0.0.1:8000/mcp"
    )

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )