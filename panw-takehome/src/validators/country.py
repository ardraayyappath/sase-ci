from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class CountryValidator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        "name",
        "capital",
        "population",
        "currencies",
        "languages",
    )
    field_types: ClassVar[dict[str, type]] = {
        "name": dict,
        "capital": list,
        "population": int,
        "currencies": dict,
        "languages": dict,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        assert data["population"] >= 0, (
            f"{cls.__name__}: population must be >= 0, got {data['population']}"
        )
