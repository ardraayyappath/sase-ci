from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class DailyWeatherValidator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        "daily",
        "timezone",
        "latitude",
        "longitude",
    )
    field_types: ClassVar[dict[str, type]] = {
        "daily": dict,
        "timezone": str,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        daily = data["daily"]

        time = daily.get("time")
        assert time and len(time) > 0, (
            f"{cls.__name__}: daily.time must be a non-empty list"
        )
        assert len(time) >= 7, (
            f"{cls.__name__}: daily.time must have >= 7 entries (one week), got {len(time)}"
        )

        temp_max = daily.get("temperature_2m_max")
        temp_min = daily.get("temperature_2m_min")

        assert temp_max and isinstance(temp_max, list), (
            f"{cls.__name__}: daily.temperature_2m_max must be a non-empty list"
        )
        assert temp_min and isinstance(temp_min, list), (
            f"{cls.__name__}: daily.temperature_2m_min must be a non-empty list"
        )

        # Arrays must be parallel — a length mismatch means values can't be
        # correlated to their timestamps, which would silently corrupt any consumer.
        assert len(temp_max) == len(time), (
            f"{cls.__name__}: daily.temperature_2m_max length ({len(temp_max)}) "
            f"does not match daily.time length ({len(time)})"
        )
        assert len(temp_min) == len(time), (
            f"{cls.__name__}: daily.temperature_2m_min length ({len(temp_min)}) "
            f"does not match daily.time length ({len(time)})"
        )

        for i, temp in enumerate(temp_max):
            # Open-Meteo uses null for missing values (e.g. station offline).
            # A null would pass the isinstance check but break the range comparison.
            assert temp is not None, (
                f"{cls.__name__}: daily.temperature_2m_max contains a null value at index {i}"
            )
            assert -80 <= temp <= 60, (
                f"{cls.__name__}: temperature_2m_max value {temp} at index {i} "
                f"outside valid range [-80, 60]"
            )

        for i, temp in enumerate(temp_min):
            assert temp is not None, (
                f"{cls.__name__}: daily.temperature_2m_min contains a null value at index {i}"
            )
            assert -80 <= temp <= 60, (
                f"{cls.__name__}: temperature_2m_min value {temp} at index {i} "
                f"outside valid range [-80, 60]"
            )

        for i, (hi, lo) in enumerate(zip(temp_max, temp_min)):
            assert hi >= lo, (
                f"{cls.__name__}: daily high ({hi}) is less than daily low ({lo}) at index {i}; "
                f"temperature_2m_max must always be >= temperature_2m_min"
            )
