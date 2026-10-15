import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "python",
            "-m",
            "backend.mcp.server",
        ],
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            print("MCP connection established!")

            # -------------------------------------------------
            # Test hotel MCP tool
            # -------------------------------------------------

            hotel_response = await session.call_tool(
                "search_hotels_mcp",
                arguments={
                    "destination": "New York",
                    "check_in": "2026-10-02",
                    "check_out": "2026-10-10",
                    "minimum_rating": 4.0,
                },
            )

            print("\nHotel search result:")
            print(hotel_response)

            print("\nIs error:")
            print(hotel_response.is_error)


if __name__ == "__main__":
    asyncio.run(main())