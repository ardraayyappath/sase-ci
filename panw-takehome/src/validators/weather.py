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
        assert len(times) >= 24, (
            f"{cls.__name__}: hourly.time must have >= 24 entries (one day), got {len(times)}"
        )

        temps = data["hourly"].get("temperature_2m", [])

        # Arrays must be parallel — a length mismatch means values can't be
        # correlated to their timestamps, which would silently corrupt any consumer.
        assert len(temps) == len(times), (
            f"{cls.__name__}: hourly.temperature_2m length ({len(temps)}) "
            f"does not match hourly.time length ({len(times)})"
        )

        for temp in temps:
            # Open-Meteo uses null for missing values (e.g. station offline).
            # A null would pass the isinstance check but break the range comparison.
            assert temp is not None, (
                f"{cls.__name__}: hourly.temperature_2m contains a null value"
            )
            assert -80 <= temp <= 60, (
                f"{cls.__name__}: temperature_2m value {temp} outside valid range [-80, 60]"
            )
