# Skill: validator-generator

Generate a `BaseValidator` subclass for a new API response shape.

## Inputs
- `sample_json` — one representative response dict
- `validator_name` — e.g. `RegionCountryValidator`
- `required_fields` — top-level keys that must always be present
- `semantic_constraints` — plain-English rules (e.g. `population >= 0`, `cca3 is 3 chars`)

## Output

A file at `src/validators/{resource}.py` with:

1. `required_fields: ClassVar[tuple[str, ...]]` — keys checked by `BaseValidator.validate`
2. `field_types: ClassVar[dict[str, type]]` — Python types inferred from sample
3. `custom_checks(cls, data)` — one assert per semantic constraint, with message

## Hard constraints

| Rule | Source |
|------|--------|
| Must subclass `BaseValidator` from `src.validators.base` | `framework-rules.md` |
| No `pydantic`, no `jsonschema` | `framework-rules.md` |
| Assertion messages must include `cls.__name__` | `code-style.md` |
| Presence checks in `required_fields` tuple, not in `custom_checks` | `validator-generator.md` |
| No network calls, no pytest fixture imports | `framework-rules.md` |

## Type inference rules

| JSON value | Python type |
|-----------|-------------|
| `{}` | `dict` |
| `[]` | `list` |
| `"string"` | `str` |
| `42` | `int` |
| `3.14` | `float` |
| `true/false` | `bool` |
| Could be multiple types | Omit from `field_types`, handle in `custom_checks` |

## Template

```python
from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class {Name}Validator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        "field_a",
        "field_b",
    )
    field_types: ClassVar[dict[str, type]] = {
        "field_a": dict,
        "field_b": str,
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        assert data["field_b"] > 0, (
            f"{cls.__name__}: field_b must be > 0, got {data['field_b']}"
        )
```

## Anti-patterns

- `from pydantic import BaseModel` — incompatible with Allure step lifecycle
- `jsonschema.validate(data, schema)` — same reason
- Presence checks inside `custom_checks` — they belong in `required_fields`
- Assertion message without `cls.__name__` — makes Allure output unreadable
