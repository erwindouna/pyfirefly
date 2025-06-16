"""Asynchronous Python client for Python Firefly."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self
from urllib.parse import urlparse

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from pyfirefly.exceptions import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyError,
    FireflyNotFoundError,
    FireflyTimeoutError,
)
from pyfirefly.models import About, Account, Bill, Budget, Category, Transaction

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
    ) -> Any:
        """Handle a request to the Python Firefly API.

        Args:
        ----
            uri: Request URI, without '/api/', for example, 'status'.
            method: HTTP method to use.
            params: Extra options to improve or limit the response.

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
            msg = f"Connection error for {method} {url}: {err}"
            raise FireflyConnectionError(msg) from err
        except (ClientError, socket.gaierror) as err:
            msg = f"Unexpected error during {method} {url}: {err}"
            raise FireflyConnectionError(msg) from err

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type and "application/vnd.api+json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Firefly API"
            raise FireflyError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.json()

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

    async def get_transactions(
        self,
        account_id: int | None = None,
        start: str | None = None,
        end: str | None = None,
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
                params["start"] = start
            if end:
                params["end"] = end

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

    async def get_categories(self, category_id: int, start: str | None = None, end: str | None = None) -> Category:
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
            params["start"] = start
        if end:
            params["end"] = end

        category = await self._request(uri=f"categories/{category_id}", params=params)
        return Category.from_dict(category["data"])

    async def get_budgets(self, start: str | None = None, end: str | None = None) -> list[Budget]:
        """Get budgets for the Firefly server. Both start and end dates are required for date range filtering.

        Args:
            start: The start date for the budgets.
            end: The end date for the budgets.

        Returns:
            A list of Budget objects containing budget information.

        """
        params: dict[str, str] = {}
        if start and end:
            params["start"] = start
            params["end"] = end

        budgets = await self._request(uri="budgets", params=params)
        return [Budget.from_dict(budget) for budget in budgets["data"]]

    async def get_bills(self, start: str | None = None, end: str | None = None) -> list[Bill]:
        """Get bills for the Firefly server. Both start and end dates are required for date range filtering.

        Args:
            start: The start date for the bills.
            end: The end date for the bills.

        Returns:
            A list of Bill containing bill information.

        """
        bills: list[dict[str, Any]] = []
        next_page: int | None = 1
        params: dict[str, str] = {"page": str(next_page)}
        if start and end:
            params["start"] = start
            params["end"] = end

        while next_page:
            response = await self._request(uri="bills", params=params)
            bills.extend(response["data"])

            pagination = response.get("meta", {}).get("pagination", {})
            current_page = int(pagination.get("current_page", 1) or 1)
            total_pages = int(pagination.get("total_pages", 1) or 1)

            next_page = current_page + 1 if current_page < total_pages else None

        return [Bill.from_dict(bill) for bill in bills]

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
