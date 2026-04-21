from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class RegionCountryValidator(BaseValidator):
    """
    Validates a single country entry returned by GET /region/{name}.

    Region queries return the same object shape as direct country lookups but
    the field guarantee is weaker — some fields (currencies, languages) may be
    absent for territories. Required fields here are the ones the region endpoint
    reliably provides for every entry.
    """

    required_fields: ClassVar[tuple[str, ...]] = (
        "name",
        "cca3",
        "region",
        "population",
        "capital",
    )
    field_types: ClassVar[dict[str, type]] = {
        "name": dict,
        "cca3": str,
        "region": str,
        "population": int,
        "capital": list,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        assert data["population"] >= 0, (
            f"{cls.__name__}: population must be >= 0, got {data['population']}"
        )
        assert len(data["region"]) > 0, (
            f"{cls.__name__}: region must be a non-empty string"
        )
        assert len(data["cca3"]) == 3, (
            f"{cls.__name__}: cca3 must be exactly 3 characters, got '{data['cca3']}'"
        )
