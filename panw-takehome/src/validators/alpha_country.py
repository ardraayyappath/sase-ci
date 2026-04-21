from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class AlphaCountryValidator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        "name",
        "cca2",
        "cca3",
        "ccn3",
        "region",
        "population",
    )
    field_types: ClassVar[dict[str, type]] = {
        "name": dict,
        "cca2": str,
        "cca3": str,
        "ccn3": str,
        "region": str,
        "population": int,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        assert len(data["cca2"]) == 2, (
            f"{cls.__name__}: cca2 must be exactly 2 characters, got {data['cca2']!r}"
        )
        assert len(data["cca3"]) == 3, (
            f"{cls.__name__}: cca3 must be exactly 3 characters, got {data['cca3']!r}"
        )
        assert data["ccn3"].isdigit(), (
            f"{cls.__name__}: ccn3 must be all digits, got {data['ccn3']!r}"
        )
        assert data["population"] >= 0, (
            f"{cls.__name__}: population must be >= 0, got {data['population']}"
        )
        common_name = data["name"].get("common")
        assert isinstance(common_name, str) and common_name, (
            f"{cls.__name__}: name.common must be a non-empty string, got {common_name!r}"
        )
