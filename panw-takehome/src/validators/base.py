from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar


class BaseValidator(ABC):
    required_fields: ClassVar[tuple[str, ...]] = ()
    field_types: ClassVar[dict[str, type]] = {}

    @classmethod
    def validate(cls, data: dict[str, Any]) -> None:
        missing = [f for f in cls.required_fields if f not in data]
        assert not missing, f"{cls.__name__}: missing fields {missing}"
        for field, expected in cls.field_types.items():
            if field in data:
                assert isinstance(data[field], expected), (
                    f"{cls.__name__}: {field} is {type(data[field]).__name__}, "
                    f"expected {expected.__name__}"
                )
        cls.custom_checks(data)

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        """Override for per-validator checks beyond type/presence."""
