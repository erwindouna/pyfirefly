"""Conftest for the pyfirefly tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from pyfirefly import Firefly


@pytest.fixture(name="firefly_client")
async def client() -> AsyncGenerator[Firefly, None]:
    """Return a pyfirefly client."""
    async with (
        ClientSession() as session,
        Firefly(
            api_url="http://localhost:9000/api/v1",
            api_key="test_api_key",
            session=session,
            request_timeout=10.0,
        ) as firefly_client,
    ):
        yield firefly_client
