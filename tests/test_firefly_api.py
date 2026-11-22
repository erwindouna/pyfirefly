"""Tests for the pyfirefly library that rely on a functioning Firefly install."""

# pylint: disable=protected-access
import os
import random
import string

import pytest

from pyfirefly import Firefly
from pyfirefly.models import Account, AccountAttributes


def random_string(length: int = 8) -> str:
    """Fixture to get a short random string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))  # noqa: S311


@pytest.fixture
def revenue_account() -> Account:
    """Return account of type revenue."""
    return Account(
        type="revenue",
        id="",
        attributes=AccountAttributes(
            name=f"test account {random_string()}",
            currency_id="1",
            currency_code="AUD",
            active=True,
            interest="0",
        ),
    )


@pytest.fixture
def expense_account() -> Account:
    """Return account of type expense."""
    return Account(
        type="expense",
        id="",
        attributes=AccountAttributes(
            name=f"test account {random_string()}",
            currency_id="1",
            currency_code="AUD",
            active=True,
            interest="0",
        ),
    )


@pytest.fixture
def asset_account() -> Account:
    """Return account of type asset."""
    return Account(
        type="asset",
        id="",
        attributes=AccountAttributes(
            name=f"test account {random_string()}",
            currency_id="1",
            currency_code="AUD",
            active=True,
            account_role="defaultAsset",
            interest="0",
        ),
    )


@pytest.fixture
def liability_account() -> Account:
    """Return account of type liability."""
    return Account(
        type="liability",
        id="",
        attributes=AccountAttributes(
            name=f"test account {random_string()}",
            currency_id="1",
            currency_code="AUD",
            active=True,
            liability_type="loan",
            liability_direction="credit",
            interest="5.3",
        ),
    )


@pytest.mark.skipif(
    "FIREFLY_TOKEN" not in os.environ or "FIREFLY_URI" not in os.environ,
    reason="Cannot access fireflyIII API unless FIREFLY_URI and FIREFLY_TOKEN provided.",
)
@pytest.mark.asyncio
async def test_create_and_delete_asset_account(asset_account: Account) -> None:  # pylint: disable=W0621
    """Test creation and deletion of an asset account."""
    async with Firefly(
        api_url=os.environ["FIREFLY_URI"],
        api_key=os.environ["FIREFLY_TOKEN"],
    ) as firefly:
        new_account = await firefly.create_account(asset_account)

        assert isinstance(new_account, Account)

        # Fetch accounts, check it worked
        firefly_accounts = await firefly.get_accounts()
        assert len(firefly_accounts) > 0
        assert asset_account.attributes.name in [i.attributes.name for i in firefly_accounts]

        # Now delete it
        await firefly.delete_account(new_account)

        # Now fetch all the accounts, and see if it's there.
        firefly_accounts = await firefly.get_accounts()
        assert asset_account.attributes.name not in [i.attributes.name for i in firefly_accounts]


@pytest.mark.skipif(
    "FIREFLY_TOKEN" not in os.environ or "FIREFLY_URI" not in os.environ,
    reason="Cannot access fireflyIII API unless FIREFLY_URI and FIREFLY_TOKEN provided.",
)
@pytest.mark.asyncio
async def test_create_and_delete_liability_account(liability_account: Account) -> None:  # pylint: disable=W0621
    """Test creation and deletion of an liability account."""
    async with Firefly(
        api_url=os.environ["FIREFLY_URI"],
        api_key=os.environ["FIREFLY_TOKEN"],
    ) as firefly:
        new_account = await firefly.create_account(liability_account)

        assert isinstance(new_account, Account)

        # Fetch accounts, check it worked
        firefly_accounts = await firefly.get_accounts()
        assert len(firefly_accounts) > 0
        assert liability_account.attributes.name in [i.attributes.name for i in firefly_accounts]

        # Now delete it
        await firefly.delete_account(new_account)

        # Now fetch all the accounts, and see if it's there.
        firefly_accounts = await firefly.get_accounts()
        assert liability_account.attributes.name not in [i.attributes.name for i in firefly_accounts]


@pytest.mark.skipif(
    "FIREFLY_TOKEN" not in os.environ or "FIREFLY_URI" not in os.environ,
    reason="Cannot access fireflyIII API unless FIREFLY_URI and FIREFLY_TOKEN provided.",
)
@pytest.mark.asyncio
async def test_create_and_delete_expense_account(expense_account: Account) -> None:  # pylint: disable=W0621
    """Test creation and deletion of an expense account."""
    async with Firefly(
        api_url=os.environ["FIREFLY_URI"],
        api_key=os.environ["FIREFLY_TOKEN"],
    ) as firefly:
        new_account = await firefly.create_account(expense_account)

        assert isinstance(new_account, Account)

        # Fetch accounts, check it worked
        firefly_accounts = await firefly.get_accounts()
        assert len(firefly_accounts) > 0
        assert expense_account.attributes.name in [i.attributes.name for i in firefly_accounts]

        # Now delete it
        await firefly.delete_account(new_account)

        # Now fetch all the accounts, and see if it's there.
        firefly_accounts = await firefly.get_accounts()
        assert expense_account.attributes.name not in [i.attributes.name for i in firefly_accounts]


@pytest.mark.skipif(
    "FIREFLY_TOKEN" not in os.environ or "FIREFLY_URI" not in os.environ,
    reason="Cannot access fireflyIII API unless FIREFLY_URI and FIREFLY_TOKEN provided.",
)
@pytest.mark.asyncio
async def test_create_and_delete_revenue_account(revenue_account: Account) -> None:  # pylint: disable=W0621
    """Test creation and deletion of an revenue account."""
    async with Firefly(
        api_url=os.environ["FIREFLY_URI"],
        api_key=os.environ["FIREFLY_TOKEN"],
    ) as firefly:
        new_account = await firefly.create_account(revenue_account)
        assert isinstance(new_account, Account)

        # Fetch accounts, check the revenue_account fixture successfully created the account
        firefly_accounts = await firefly.get_accounts()
        assert len(firefly_accounts) > 0
        assert new_account.attributes.name in [i.attributes.name for i in firefly_accounts]

        # Now delete it
        await firefly.delete_account(new_account)

        # Now fetch all the accounts, and see if it's there.
        firefly_accounts = await firefly.get_accounts()
        assert new_account.attributes.name not in [i.attributes.name for i in firefly_accounts]
