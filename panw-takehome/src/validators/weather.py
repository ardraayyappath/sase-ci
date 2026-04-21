from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class WeatherValidator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        "hourly",
        "timezone",
        "latitude",
        "longitude",
    )
    field_types: ClassVar[dict[str, type]] = {
        "hourly": dict,
        "timezone": str,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        times = data["hourly"].get("time")
        assert times and len(times) > 0, (
            f"{cls.__name__}: hourly.time must be a non-empty list"
        )
        for temp in data["hourly"].get("temperature_2m", []):
            assert -80 <= temp <= 60, (
                f"{cls.__name__}: temperature_2m value {temp} outside valid range [-80, 60]"
            )
