"""Asynchronous example for the dev server."""

import asyncio

from pyfirefly import Firefly


async def main() -> None:
    """Run the example."""
    async with Firefly(
        api_url="http://localhost:9000",
        api_key="YOUR_API_KEY",
    ) as firefly:
        about_info = await firefly.get_about()
        print("Firefly About Information:", about_info)


if __name__ == "__main__":
    asyncio.run(main())
