# Skill: test-generator

Generate a pytest test file for one endpoint in the panw-takehome framework.

## Inputs
- `endpoint_path` — e.g. `/region/{name}`
- `http_method` — GET | POST
- `environment` — `countries` | `weather`
- `expected_response_fields` — top-level keys to validate
- `negative_cases` — list of `{description, params}` that should return 4xx

## Output

A file at `tests/{environment}/test_{resource}.py` containing:

1. **Positive test** — asserts HTTP 200 and `len(results) >= env_client.config.min_results_count`
2. **Schema test** — calls `{Validator}.validate(results[0])` using a class from `src/validators/`
3. **Negative tests** — parametrized from `test_data/*.json`, marked `@pytest.mark.negative`

## Hard constraints

| Rule | Source |
|------|--------|
| Use `env_client` fixture — never instantiate `EnvironmentClient` directly | `framework-rules.md` |
| No `import requests` | `framework-rules.md` |
| No `import time`, no manual elapsed assertion | `testing-standards.md` |
| Parametrize data lives in `test_data/*.json`, never inlined | `testing-standards.md` |
| `allure.step` for logical phases only; request steps emitted by `EnvironmentClient` | `framework-rules.md` |
| `pytest.param(..., id=...)` on all parametrize calls | `testing-standards.md` |

## Template

```python
from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.{module} import {Validator}

_DATA = json.loads((Path(__file__).resolve().parents[2] / "test_data" / "{data}.json").read_text())
_CASES = _DATA["{key}"]


def test_{name}_returns_valid_payload(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch"):
        resp = env_client.get("{path}")
    assert resp.status_code == 200
    results = resp.json() if isinstance(resp.json(), list) else [resp.json()]
    assert len(results) >= env_client.config.min_results_count
    with allure.step("Validate schema"):
        {Validator}.validate(results[0])


@pytest.mark.negative
@pytest.mark.parametrize("bad", [pytest.param(c, id=c["description"]) for c in _CASES])
def test_{name}_rejects_invalid(env_client: EnvironmentClient, bad: dict) -> None:
    with allure.step(f"Fetch with invalid input: {bad['description']}"):
        resp = env_client.get("{path}", params=bad["params"])
    assert resp.status_code >= 400
```

## Anti-patterns

- `requests.get(...)` — use `env_client.get(...)`
- `time.monotonic()` — SLA enforced automatically by `EnvironmentClient._request`
- `@pytest.mark.parametrize("city", ["London", "Tokyo"])` — load from `test_data/cities.json`
- Hardcoded base URL or threshold — those live in `config/environments.yaml`
