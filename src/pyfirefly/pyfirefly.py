"""Asynchronous Python client for Python Firefly."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from datetime import datetime
from importlib import metadata
from typing import Any, Self
from urllib.parse import urlparse

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST
from yarl import URL

from pyfirefly.exceptions import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyError,
    FireflyNotFoundError,
    FireflyTimeoutError,
)
from pyfirefly.models import (
    About,
    Account,
    AccountAttributes,
    Bill,
    Budget,
    BudgetLimitAttributes,
    Category,
    Currency,
    Preferences,
    Transaction,
)

try:
    VERSION = metadata.version(__package__)
except metadata.PackageNotFoundError:
    VERSION = "DEV-0.0.0"


@dataclass
class Firefly:
    """Main class for handling connections with the Python Firefly API."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    def __init__(
        self,
        api_url: str,
        api_key: str,
        *,
        request_timeout: float = 10.0,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize the Firefly object.

        Args:
        ----
            api_url: URL of the Firefly API.
            api_key: API key for authentication.
            request_timeout: Timeout for requests (in seconds).
            session: Optional aiohttp session to use.

        """
        self._api_key = api_key
        self._request_timeout = request_timeout
        self._session = session

        parsed_url = urlparse(api_url)
        self._api_host = parsed_url.hostname or "localhost"
        self._api_scheme = parsed_url.scheme or "http"
        self._api_port = parsed_url.port or 9000

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
        data: Any = None,
    ) -> Any:
        """Handle a request to the Python Firefly API.

        Args:
        ----
            uri: Request URI, without '/api/', for example, 'status'.
            method: HTTP method to use.
            params: Extra options to improve or limit the response.
            data: Data to send if method is METH_POST

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the Python Firefly API.

        Raises:
        ------
            Python FireflyAuthenticationError: If the API key is invalid.

        """
        url = URL.build(
            scheme=self._api_scheme,
            host=self._api_host,
            port=self._api_port,
            path="/api/v1/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonFirefly/{VERSION}",
            "Authorization": f"Bearer {self._api_key}",
        }

        if self._session is None:
            self._session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self._request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                )
                response.raise_for_status()
        except TimeoutError as err:
            msg = f"Timeout error while accessing {method} {url}: {err}"
            raise FireflyTimeoutError(msg) from err
        except ClientResponseError as err:
            if err.status == 401:
                msg = f"Authentication failed for {method} {url}: Invalid API key"
                raise FireflyAuthenticationError(msg) from err
            if err.status == 404:
                msg = f"Resource not found at {method} {url}: {err}"
                raise FireflyNotFoundError(msg) from err
            if err.status == 422:
                json_response = await response.json()
                msg = f"Validation error for POST to {url}. "
                msg += " ".join([i[0] for i in json_response["errors"].values()])
                raise FireflyError(msg) from err
            msg = f"Connection error for {method} {url}: {err}"
            raise FireflyConnectionError(msg) from err
        except (ClientError, socket.gaierror) as err:
            msg = f"Unexpected error during {method} {url}: {err}"
            raise FireflyConnectionError(msg) from err

        if response.status == 204:
            # Must have been a METH_DELETE. There is no data to return, so return early.
            return None

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type and "application/vnd.api+json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Firefly API"
            raise FireflyError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.json()

    def _format_date(self, date_value: datetime | str) -> str:
        """Format a date value to a string in 'YYYY-MM-DD' format.

        Args:
            date_value: A date object or a string representing a date.

        Returns:
            A string formatted as 'YYYY-MM-DD'.

        """
        if isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        return date_value

    async def get_about(self) -> About:
        """Get information about the Firefly server.

        Returns
        -------
            An About object with information about the Firefly server.

        """
        about = await self._request("about")
        return About.from_dict(about["data"])

    async def get_accounts(self) -> list[Account]:
        """Get a list of accounts from the Firefly server.

        Returns
        -------
            A list of Account objects containing account information.

        """
        accounts: list[dict[str, str]] = []
        next_page: int | None = 1

        while next_page:
            response = await self._request(
                uri="accounts",
                method="GET",
                params={"page": next_page},
            )

            accounts.extend(response["data"])

            # Check for the next page in the pagination metadata
            pagination = response.get("meta", {}).get("pagination", {})
            current_page = int(pagination.get("current_page", 1) or 1)
            total_pages = int(pagination.get("total_pages", 1) or 1)

            next_page = current_page + 1 if current_page < total_pages else None

        return [Account.from_dict(acc) for acc in accounts]

    async def delete_account(self, account: Account) -> None:
        """Delete a account.

        Args:
        ----
            account: Account object to delete.

        """
        uri = f"accounts/{account.id}"

        await self._request(
            uri=uri,
            method=METH_DELETE,
        )

    async def create_account(self, account: Account) -> Account:
        """Create a account.

        Args:
        ----
            account: Account object to create. id attribute is ignored.

        Returns:
        -------
            A new account object, with the id attribute set.

        """
        uri = "accounts"

        # translate account object into a data structure that is acceptable to
        # aiohttp post() method. THe documentation says this is can be a FormData
        # object or anything that can be passed into FormData, e.g. a dictionary,
        # bytes, or file-like object.
        # But also the fireflyiii /v1/accounts POST API endpoint is expecting a json
        # array with the necessary account information or key=value pairs, and
        # gives an example.

        response = await self._request(
            uri=uri,
            method=METH_POST,
            data={
                "type": account.type,
                "name": account.attributes.name,
                "currency_id": account.attributes.currency_id,
                "currency_code": account.attributes.currency_code,
                "include_net_worth": True,
                "notes": account.attributes.notes,
                "account_role": account.attributes.account_role,
                "liability_type": account.attributes.liability_type,
                "liability_direction": account.attributes.liability_direction,
                "iban": account.attributes.iban,
                "bic": account.attributes.bic,
                "account_number": account.attributes.account_number,
                "opening_balance": account.attributes.opening_balance,
                "opening_balance_date": account.attributes.opening_balance_date,
                "virtual_balance": account.attributes.virtual_balance,
                "active": account.attributes.active,
                "order": account.attributes.order,
                "credit_card_type": account.attributes.credit_card_type,
                "monthly_payment_date": account.attributes.monthly_payment_date,
                "interest": float(account.attributes.interest) if account.attributes.interest is not None else 0.0,
                "interest_period": account.attributes.interest_period,
                "latitude": account.attributes.latitude,
                "longitude": account.attributes.longitude,
                "zoom_level": account.attributes.zoom_level,
            },
        )

        # Turn these into the FireFly Account object.  Some data returned doesn't fit into that class.
        data_dict = response["data"]
        dd_a = data_dict["attributes"]
        del data_dict["links"]
        aa = AccountAttributes(
            created_at=dd_a["created_at"],
            updated_at=dd_a["updated_at"],
            active=dd_a["active"],
            name=dd_a["name"],
            type=dd_a["type"],
            account_role=dd_a["account_role"],
            currency_id=dd_a["currency_id"],
            currency_code=dd_a["currency_code"],
            currency_symbol=dd_a["currency_symbol"],
            currency_decimal_places=dd_a["currency_decimal_places"],
            native_currency_id=dd_a.get("native_currency_id", None),
            native_currency_code=dd_a.get("native_currency_code", None),
            native_currency_symbol=dd_a.get("native_currency_symbol", None),
            native_currency_decimal_places=dd_a.get("native_currency_decimal_places", None),
            current_balance=dd_a["current_balance"],
            native_current_balance=dd_a.get("native_current_balance", None),
            current_balance_date=dd_a["current_balance_date"],
            order=dd_a["order"],
            notes=dd_a["notes"],
            monthly_payment_date=dd_a["monthly_payment_date"],
            credit_card_type=dd_a["credit_card_type"],
            account_number=dd_a["account_number"],
            iban=dd_a["iban"],
            bic=dd_a["bic"],
            virtual_balance=dd_a["virtual_balance"],
            native_virtual_balance=dd_a.get("native_virtual_balance", None),
            opening_balance=dd_a["opening_balance"],
            native_opening_balance=dd_a.get("native_opening_balance", None),
            opening_balance_date=dd_a["opening_balance_date"],
            liability_type=dd_a["liability_type"],
            liability_direction=dd_a["liability_direction"],
            interest=dd_a["interest"],
            interest_period=dd_a["interest_period"],
            current_debt=dd_a.get("current_debt", None),
            include_net_worth=dd_a["include_net_worth"],
            longitude=dd_a["longitude"],
            latitude=dd_a["latitude"],
            zoom_level=dd_a["zoom_level"],
            last_activity=dd_a["last_activity"],
        )
        data_dict["attributes"] = aa
        return Account(**data_dict)

    async def get_transactions(
        self,
        account_id: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Transaction]:
        """Get transactions for a specific account. Else, return all transactions.

        Args:
        ----
            account_id: The ID of the account to retrieve transactions for.
            start: The start date for the transactions.
            end: The end date for the transactions.

        Returns:
        -------
            A list of transactions for the specified account.

        """
        transactions: list[dict[str, Any]] = []
        next_page: int | None = 1

        uri = f"accounts/{account_id}/transactions"
        if account_id is None:
            uri = "transactions"

        while next_page:
            params: dict[str, str] = {"page": str(next_page)}
            if start:
                params["start"] = self._format_date(start)
            if end:
                params["end"] = self._format_date(end)

            response = await self._request(
                uri=uri,
                method="GET",
                params=params,
            )

            transactions.extend(response["data"])

            pagination = response.get("meta", {}).get("pagination", {})
            current_page = int(pagination.get("current_page", 1) or 1)
            total_pages = int(pagination.get("total_pages", 1) or 1)

            next_page = current_page + 1 if current_page < total_pages else None

        return [Transaction.from_dict(tx) for tx in transactions]

    async def get_categories(self) -> list[Category]:
        """Get all categories from the Firefly server.

        Returns
        -------
            A list of Category objects containing category information.

        """
        categories: list[dict[str, str]] = []
        next_page: int | None = 1

        while next_page:
            response = await self._request(
                uri="categories",
                method="GET",
                params={"page": next_page},
            )

            categories.extend(response["data"])

            pagination = response.get("meta", {}).get("pagination", {})
            current_page = int(pagination.get("current_page", 1) or 1)
            total_pages = int(pagination.get("total_pages", 1) or 1)

            next_page = current_page + 1 if current_page < total_pages else None

        return [Category.from_dict(cat) for cat in categories]

    async def get_category(
        self,
        category_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Category:
        """Get a specific category by its ID.

        Args:
            category_id: The ID of the category to retrieve.
            start: The start date for the category, to show spent and earned info.
            end: The end date for the category, to show spent and earned info.

        Returns:
            A Category object containing the category information.

        """
        params: dict[str, str] = {}
        if start:
            params["start"] = self._format_date(start)
        if end:
            params["end"] = self._format_date(end)

        category = await self._request(uri=f"categories/{category_id}", params=params)
        return Category.from_dict(category["data"])

    async def get_budgets(self, start: datetime | None = None, end: datetime | None = None) -> list[Budget]:
        """Get budgets for the Firefly server. Both start and end dates are required for date range filtering.

        Args:
            start: The start date for the budgets.
            end: The end date for the budgets.

        Returns:
            A list of Budget objects containing budget information.

        """
        params: dict[str, str] = {}
        if start and end:
            params["start"] = self._format_date(start)
            params["end"] = self._format_date(end)

        budgets = await self._request(uri="budgets", params=params)
        return [Budget.from_dict(budget) for budget in budgets["data"]]

    async def get_budget_limits(self, budget_id: int, start: datetime | None = None, end: datetime | None = None) -> list[BudgetLimitAttributes]:
        """Get budget limits for the Firefly server. Both start and end dates are required for date range filtering.

        Args:
            budget_id: The ID of the budget to retrieve limits for.
            start: The start date for the budget limits.
            end: The end date for the budget limits.

        Returns:
            A list of BudgetLimitAttributes objects containing budget limit information.

        """
        params: dict[str, str] = {}
        if start and end:
            params["start"] = self._format_date(start)
            params["end"] = self._format_date(end)

        budget_limits = await self._request(uri=f"budgets/{budget_id}/limits", params=params)
        return [BudgetLimitAttributes.from_dict(limit) for limit in budget_limits["data"]]

    async def get_bills(self, start: datetime | None = None, end: datetime | None = None) -> list[Bill]:
        """Get bills for the Firefly server. Both start and end dates are required for date range filtering.

        Args:
            start: The start date for the bills.
            end: The end date for the bills.

        Returns:
            A list of Bill containing bill information.

        """
        bills: list[dict[str, Any]] = []
        next_page: int | None = 1

        while next_page:
            params: dict[str, str] = {"page": str(next_page)}
            if start and end:
                params["start"] = self._format_date(start)
                params["end"] = self._format_date(end)

            response = await self._request(uri="bills", params=params)
            bills.extend(response["data"])

            pagination = response.get("meta", {}).get("pagination", {})
            current_page = int(pagination.get("current_page", 1) or 1)
            total_pages = int(pagination.get("total_pages", 1) or 1)

            next_page = current_page + 1 if current_page < total_pages else None

        return [Bill.from_dict(bill) for bill in bills]

    async def get_preferences(self) -> list[Preferences]:
        """Get preferences from the Firefly server.

        Returns
        -------
            A list of Preferences objects containing the preferences.

        """
        preferences = await self._request("preferences")
        return [Preferences.from_dict(pref) for pref in preferences["data"]]

    async def get_currencies(self) -> list[Currency]:
        """Get currencies from the Firefly server.

        Returns
        -------
            A list of Currency objects containing the currencies.

        """
        currencies = await self._request("currencies")
        return [Currency.from_dict(cur) for cur in currencies["data"]]

    async def get_currency_primary(self) -> Currency:
        """Get the primary currency of the current administration.

        Returns
        -------
            A Currency object containing the primary currency symbol.

        """
        currency = await self._request("currencies/primary")
        return Currency.from_dict(currency["data"])

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Firefly object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
