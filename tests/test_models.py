"""Test the models of the Firefly API client."""

from __future__ import annotations

from datetime import datetime, timezone
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

    transactions = await firefly_client.get_transactions(
        account_id=1,
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 12, 31, tzinfo=timezone.utc),
    )
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

    category = await firefly_client.get_category(
        category_id=1,
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 12, 31, tzinfo=timezone.utc),
    )
    assert category == snapshot

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

    category = await firefly_client.get_category(category_id=1)
    assert category == snapshot


async def test_categories_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Categories model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/categories",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("categories.json"),
        ),
    )

    categories = await firefly_client.get_categories()
    assert categories == snapshot


async def test_budgets_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Budgets model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/budgets",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("budgets.json"),
        ),
    )

    budgets = await firefly_client.get_budgets(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 12, 31, tzinfo=timezone.utc),
    )
    assert budgets == snapshot

    # Now without a date range
    aresponses.add(
        "localhost:9000",
        "/api/v1/budgets",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("budgets.json"),
        ),
    )

    budgets = await firefly_client.get_budgets()
    assert budgets == snapshot


async def test_bills_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Bills model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/bills",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("bills.json"),
        ),
    )

    bills = await firefly_client.get_bills(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 12, 31, tzinfo=timezone.utc),
    )
    assert bills == snapshot

    # Now without a date range
    aresponses.add(
        "localhost:9000",
        "/api/v1/bills",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("bills.json"),
        ),
    )

    bills = await firefly_client.get_bills()
    assert bills == snapshot


async def test_preferences_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Preferences model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/preferences",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("preferences.json"),
        ),
    )

    preferences = await firefly_client.get_preferences()
    assert preferences == snapshot


async def test_currencies_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Currencies model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/currencies",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("currencies.json"),
        ),
    )

    currencies = await firefly_client.get_currencies()
    assert currencies == snapshot


async def test_currency_native_model(
    aresponses: ResponsesMockServer,
    firefly_client: Firefly,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Currency Native model."""
    aresponses.add(
        "localhost:9000",
        "/api/v1/currencies/native",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/vnd.api+json"},
            text=load_fixtures("currency_native.json"),
        ),
    )

    currency_native = await firefly_client.get_currency_native()
    assert currency_native == snapshot
