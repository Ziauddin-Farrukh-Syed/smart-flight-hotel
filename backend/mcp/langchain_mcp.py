from mcp import Client, StdioServerParameters


def create_server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command="uv",
        args=[
            "run",
            "python",
            "-m",
            "backend.mcp.server",
        ],
    )


async def call_mcp_tool(
    tool_name: str,
    arguments: dict,
):
    server_params = create_server_parameters()

    async with Client(server_params) as client:
        result = await client.call_tool(
            tool_name,
            arguments,
        )

        return result


async def search_flights_mcp(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str = "economy",
):
    result = await call_mcp_tool(
        "search_flights_mcp",
        {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "cabin_class": cabin_class,
        },
    )

    return result.structured_content


async def search_hotels_mcp(
    destination: str,
    check_in: str,
    check_out: str,
    minimum_rating: float = 1.0,
):
    result = await call_mcp_tool(
        "search_hotels_mcp",
        {
            "destination": destination,
            "check_in": check_in,
            "check_out": check_out,
            "minimum_rating": minimum_rating,
        },
    )

    return result.structured_content