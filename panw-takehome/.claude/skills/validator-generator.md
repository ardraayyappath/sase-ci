# Skill: Generate a BaseValidator subclass from a sample JSON response

## Input
- `sample_json`: a dict (one representative response)
- `required_fields`: which top-level keys must always be present
- `semantic_constraints`: free-text list (e.g. "population > 0", "temperature between -80 and 60")

## Output
A file at `src/validators/{resource}.py` that defines a class extending `BaseValidator` with:
1. `required_fields` tuple containing all required keys.
2. `field_types` dict mapping field names to their Python types (inferred from sample).
3. `custom_checks` classmethod implementing each semantic constraint with a clear assertion message.

## Rules
- Always subclass `BaseValidator` from `src.validators.base`.
- Never use `pydantic` or `jsonschema`.
- Type inference: `dict` for JSON objects, `list` for JSON arrays, `int`/`float`/`str`/`bool`
  as appropriate. If a value could be multiple types, omit it from `field_types` and check
  it in `custom_checks`.
- Assertion messages must name the validator class and the field:
  `f"{cls.__name__}: <field> <what failed>"`

## Template

```python
from __future__ import annotations

from typing import Any, ClassVar

from src.validators.base import BaseValidator


class {ResourceName}Validator(BaseValidator):
    required_fields: ClassVar[tuple[str, ...]] = (
        {field_list}
    )
    field_types: ClassVar[dict[str, type]] = {
        {field_type_map}
    }

    @classmethod
    def custom_checks(cls, data: dict[str, Any]) -> None:
        {semantic_assertions}
```

## Anti-patterns to reject

- `from pydantic import BaseModel` — use `BaseValidator`
- `jsonschema.validate(...)` — use `BaseValidator`
- Omitting `cls.__name__` from assertion messages — always include it for Allure readability
- Putting `required_fields` checks inside `custom_checks` — they belong in the tuple
