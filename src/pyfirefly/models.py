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
