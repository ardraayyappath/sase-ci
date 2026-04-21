# Python Code Style

## Type hints
All public functions and methods carry full type hints. Use `from __future__ import annotations`
at the top of every module for deferred evaluation.

## Dataclasses
- Config-like objects (read-only after construction): `@dataclass(frozen=True)`
- Mutable state objects: `@dataclass` (no frozen)

## No print / no logging in tests
Use `allure.attach` to surface diagnostic data. Never use `print()` or `logging` inside
test files or framework modules.

## Import order (enforced by ruff)
```
stdlib
third-party
src.*
tests.*
```

## Custom exceptions
Subclass the semantically nearest stdlib or pytest exception:
- `SLAViolation(AssertionError)` → pytest reports it as a **test failure**, not an internal error.
- `ConfigError(ValueError)` → appropriate for bad config at load time.

## Filesystem paths
Use `pathlib.Path` objects everywhere. Never concatenate string paths with `+` or `os.path.join`.

## Line length
100 characters (enforced by ruff, configured in `pyproject.toml`).
