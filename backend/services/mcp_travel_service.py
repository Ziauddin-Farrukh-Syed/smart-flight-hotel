import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def call_mcp_tool(
    tool_name: str,
    arguments: dict,
):
    """
    Connect to the MCP server and call one MCP tool.
    """

    async with streamable_http_client(
        MCP_SERVER_URL
    ) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            if result.is_error:
                raise RuntimeError(
                    f"MCP tool '{tool_name}' failed: {result}"
            )

            return result


def extract_mcp_data(result) -> dict:
    """
    Safely extract structured data from an MCP CallToolResult.

    Supports structured_content when available and
    falls back to text content.
    """

    # MCP uses snake_case.
    structured_content = getattr(
        result,
        "structured_content",
        None,
    )

    if structured_content is not None:
        return structured_content

    # Fallback: inspect text content.
    for item in result.content:

        text_value = getattr(
            item,
            "text",
            None,
        )

        if text_value is None:
            continue

        try:
            return json.loads(text_value)

        except json.JSONDecodeError:
            continue

    raise ValueError(
        "MCP returned no usable structured or JSON content."
    )


async def search_flights_via_mcp(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str,
) -> dict:

    result = await call_mcp_tool(
        "search_flights_mcp",
        {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "cabin_class": cabin_class,
        },
    )

    return extract_mcp_data(result)


async def search_hotels_via_mcp(
    destination: str,
    hotel_min_rating: float,
) -> dict:

    result = await call_mcp_tool(
        "search_hotels_mcp",
        {
            "destination": destination,
            "hotel_min_rating": hotel_min_rating,
        },
    )

    return extract_mcp_data(result)