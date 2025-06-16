"""Test the models of the Firefly API client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from tests import load_fixtures

if TYPE_CHECKING:
    from pyfirefly import Firefly
    from pyfirefly.models import About


async def test_about_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the About model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/about",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("about.json"),
        ),
    )

    about: About = await firefly_client.get_about()
    assert about == snapshot
    await firefly_client.close()
