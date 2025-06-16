"""Models for the Firefly API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


@dataclass
class Transaction(DataClassORJSONMixin):  # pylint: disable=too-many-instance-attributes
    """Model for a Firefly transaction."""

    user: str | None = None
    transaction_journal_id: str | None = None
    type: str | None = None
    date: str | None = None
    order: int | None = None
    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_name: str | None = None
    currency_decimal_places: int | None = None
    foreign_currency_id: str | None = None
    foreign_currency_code: str | None = None
    foreign_currency_symbol: str | None = None
    foreign_currency_decimal_places: int | None = None
    amount: str | None = None
    foreign_amount: str | None = None
    description: str | None = None
    source_id: str | None = None
    source_name: str | None = None
    source_iban: str | None = None
    source_type: str | None = None
    destination_id: str | None = None
    destination_name: str | None = None
    destination_iban: str | None = None
    destination_type: str | None = None
    budget_id: str | None = None
    budget_name: str | None = None
    category_id: str | None = None
    category_name: str | None = None
    bill_id: str | None = None
    bill_name: str | None = None
    reconciled: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    internal_reference: str | None = None
    external_id: str | None = None
    external_url: str | None = None
    original_source: str | None = None
    recurrence_id: str | None = None
    recurrence_total: int | None = None
    recurrence_count: int | None = None
    bunq_payment_id: str | None = None
    import_hash_v2: str | None = None
    sepa_cc: str | None = None
    sepa_ct_op: str | None = None
    sepa_ct_id: str | None = None
    sepa_db: str | None = None
    sepa_country: str | None = None
    sepa_ep: str | None = None
    sepa_ci: str | None = None
    sepa_batch_id: str | None = None
    interest_date: str | None = None
    book_date: str | None = None
    process_date: str | None = None
    due_date: str | None = None
    payment_date: str | None = None
    invoice_date: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zoom_level: int | None = None
    has_attachments: bool | None = None


@dataclass
class TransactionAttributes(DataClassORJSONMixin):
    """Attributes of a Firefly transaction."""

    created_at: str | None = None
    updated_at: str | None = None
    user: str | None = None
    group_title: str | None = None
    transactions: list[Transaction] | None = None


@dataclass
class TransactionResource(DataClassORJSONMixin):
    """Model for a Firefly transaction resource."""

    type: str
    id: str
    attributes: TransactionAttributes
    links: dict[str, Any] | None = None


@dataclass
class CategoryAmount(DataClassORJSONMixin):
    """Model for a category amount in Firefly."""

    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_decimal_places: int | None = None
    sum: str | None = None


@dataclass
class CategoryAttributes(DataClassORJSONMixin):
    """Attributes of a Firefly category."""

    created_at: str | None = None
    updated_at: str | None = None
    name: str | None = None
    notes: str | None = None
    native_currency_id: str | None = None
    native_currency_code: str | None = None
    native_currency_symbol: str | None = None
    native_currency_decimal_places: int | None = None
    spent: list[CategoryAmount] | None = None
    earned: list[CategoryAmount] | None = None


@dataclass
class Category(DataClassORJSONMixin):
    """Model for a Firefly category."""

    type: str
    id: str
    attributes: CategoryAttributes


@dataclass
class BudgetSpent(DataClassORJSONMixin):
    """Model for a Firefly budget spent."""

    sum: str | None = None
    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_decimal_places: int | None = None


@dataclass
class BudgetAttributes(DataClassORJSONMixin):
    """Attributes of a Firefly budget."""

    created_at: str | None = None
    updated_at: str | None = None
    name: str | None = None
    active: bool | None = None
    notes: str | None = None
    order: int | None = None
    auto_budget_type: str | None = None
    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_decimal_places: int | None = None
    native_currency_id: str | None = None
    native_currency_code: str | None = None
    native_currency_symbol: str | None = None
    native_currency_decimal_places: int | None = None
    auto_budget_amount: str | None = None
    native_auto_budget_amount: str | None = None
    auto_budget_period: str | None = None
    spent: list[BudgetSpent] | None = None


@dataclass
class Budget(DataClassORJSONMixin):
    """Model for a Firefly budget."""

    type: str
    id: str
    attributes: BudgetAttributes


@dataclass
class BillPaidDate(DataClassORJSONMixin):
    """Model for a Firefly bill paid date."""

    transaction_group_id: str | None = None
    transaction_journal_id: str | None = None
    date: str | None = None


@dataclass
class BillAttributes(DataClassORJSONMixin):  # pylint: disable=too-many-instance-attributes
    """Attributes of a Firefly bill."""

    created_at: str | None = None
    updated_at: str | None = None
    currency_id: str | None = None
    currency_code: str | None = None
    currency_symbol: str | None = None
    currency_decimal_places: int | None = None
    native_currency_id: str | None = None
    native_currency_code: str | None = None
    native_currency_symbol: str | None = None
    native_currency_decimal_places: int | None = None
    name: str | None = None
    amount_min: str | None = None
    amount_max: str | None = None
    native_amount_min: str | None = None
    native_amount_max: str | None = None
    date: str | None = None
    end_date: str | None = None
    extension_date: str | None = None
    repeat_freq: str | None = None
    skip: int | None = None
    active: bool | None = None
    order: int | None = None
    notes: str | None = None
    next_expected_match: str | None = None
    next_expected_match_diff: str | None = None
    object_group_id: str | None = None
    object_group_order: int | None = None
    object_group_title: str | None = None
    pay_dates: list[str] | None = None
    paid_dates: list[BillPaidDate] | None = None


@dataclass
class Bill(DataClassORJSONMixin):
    """Model for a Firefly bill."""

    type: str
    id: str
    attributes: BillAttributes
