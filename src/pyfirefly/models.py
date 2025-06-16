"""Models for the Firefly API."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class About(DataClassORJSONMixin):
    """Model for the Firefly About information."""

    version: str = field(metadata=field_options(alias="version"))
    api_version: str = field(metadata=field_options(alias="api_version"))
    php_version: str = field(metadata=field_options(alias="php_version"))
    os: str = field(metadata=field_options(alias="os"))
    driver: str = field(metadata=field_options(alias="driver"))


@dataclass
class Accounts(DataClassORJSONMixin):
    """Model for the Firefly Accounts information."""

    id: int = field(metadata=field_options(alias="id"))
    name: str = field(metadata=field_options(alias="name"))
    type: str = field(metadata=field_options(alias="type"))
    balance: float = field(metadata=field_options(alias="balance"))
    currency: str = field(metadata=field_options(alias="currency"))
    active: bool = field(metadata=field_options(alias="active"))


@dataclass
class AccountAttributes(DataClassORJSONMixin):  # pylint: disable=too-many-instance-attributes
    """Attributes of a Firefly account."""

    created_at: str | None = None
    updated_at: str | None = None
    active: bool | None = None

    name: str | None = None
    type: str | None = None
    account_role: str | None = None
    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_decimal_places: int | None = None
    native_currency_id: str | None = None
    native_currency_code: str | None = None
    native_currency_symbol: str | None = None
    native_currency_decimal_places: int | None = None
    current_balance: str | None = None
    native_current_balance: str | None = None
    current_balance_date: str | None = None
    order: int | None = None
    notes: str | None = None
    monthly_payment_date: str | None = None
    credit_card_type: str | None = None
    account_number: str | None = None
    iban: str | None = None
    bic: str | None = None
    virtual_balance: str | None = None
    native_virtual_balance: str | None = None
    opening_balance: str | None = None
    native_opening_balance: str | None = None
    opening_balance_date: str | None = None
    liability_type: str | None = None
    liability_direction: str | None = None
    interest: str | None = None
    interest_period: str | None = None
    current_debt: str | None = None
    include_net_worth: bool | None = None
    longitude: float | None = None
    latitude: float | None = None
    zoom_level: int | None = None
    last_activity: str | None = None


@dataclass
class Account(DataClassORJSONMixin):
    """Model for a Firefly account."""

    type: str
    id: str
    attributes: AccountAttributes
