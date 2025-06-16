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


async def test_accounts_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Accounts model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/accounts",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("accounts.json"),
        ),
    )

    accounts = await firefly_client.get_accounts()
    assert accounts == snapshot


async def test_account_transactions_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Account Transactions model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/accounts/1/transactions",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("account_transactions.json"),
        ),
    )

    transactions = await firefly_client.get_transactions(account_id=1, start="2025-01-01", end="2025-12-31")
    assert transactions == snapshot

    # Now for all transactions
    aresponses.add(
        "localhost:9000",
        "/api/v1/transactions",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("account_transactions.json"),
        ),
    )

    transactions = await firefly_client.get_transactions()
    assert transactions == snapshot


async def test_category_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Category model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/categories/1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("category.json"),
        ),
    )

    categories = await firefly_client.get_categories(category_id=1, start="2025-01-01", end="2025-12-31")
    assert categories == snapshot

    # Now without a date range
    aresponses.add(
        "localhost:9000",
        "/api/v1/categories/1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("category.json"),
        ),
    )

    categories = await firefly_client.get_categories(category_id=1)
    assert categories == snapshot
