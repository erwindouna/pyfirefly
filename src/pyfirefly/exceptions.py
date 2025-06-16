"""Asynchronous Python client for Python Firefly."""


class FireflyError(Exception):
    """Generic exception for Firefly errors."""


class FireflyConnectionError(FireflyError):
    """Exception raised for connection errors."""


class FireflyTimeoutError(FireflyError):
    """Exception raised for timeout errors."""


class FireflyAuthenticationError(FireflyError):
    """Exception raised for authentication errors."""


class FireflyNotFoundError(FireflyError):
    """Exception raised when a resource is not found."""
