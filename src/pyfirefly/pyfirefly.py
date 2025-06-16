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
from pyfirefly.models import About

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
        if "application/json" not in content_type:
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
