# Skill: Generate a pytest test file for a new endpoint

## Input
- `endpoint_path`: e.g. `/region/europe`
- `http_method`: GET | POST | etc.
- `environment`: `countries` | `weather`
- `expected_response_fields`: list of top-level keys
- `negative_cases`: list of `{description, request_modification}`

## Output
A file at `tests/{environment}/test_{resource}.py` that:
1. Uses the `env_client` fixture. Never instantiates its own client.
2. Has one positive test asserting 200 + `len(resp.json()) >= env_client.config.min_results_count`.
3. Has one schema test using a `BaseValidator` subclass from `src/validators/`.
4. Has parametrized negative tests marked `@pytest.mark.negative`.
5. Uses `allure.step` for logical phases ("fetch", "validate"), not per-request.
6. Does NOT hardcode base URL, threshold, or any expected count above `min_results_count`.
7. Does NOT import `requests`.
8. Does NOT import `time` or measure elapsed manually.

## Template

```python
from __future__ import annotations

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.{module} import {ValidatorClass}


@pytest.fixture(autouse=True)
def _{environment}_only(env_name: str) -> None:
    if env_name != "{environment}":
        pytest.skip(f"{environment} tests do not apply to env '{env_name}'")


def test_{endpoint_name}_returns_valid_payload(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch"):
        resp = env_client.{method}("{path}")
    assert resp.status_code == 200
    payload = resp.json()
    results = payload if isinstance(payload, list) else [payload]
    assert len(results) >= env_client.config.min_results_count
    with allure.step("Validate schema"):
        {ValidatorClass}.validate(results[0])


@pytest.mark.negative
@pytest.mark.parametrize("bad_input", [...], ids=[...])
def test_{endpoint_name}_rejects_invalid(env_client: EnvironmentClient, bad_input: dict) -> None:
    resp = env_client.{method}("{path}", params=bad_input)
    assert resp.status_code >= 400
```

## Anti-patterns to reject

- `requests.get(...)` in a test — use `env_client.get(...)`
- `time.time()` or `time.monotonic()` — SLA is automatic
- Inline parametrize data that belongs in `test_data/`
- Importing from another test file
- Hardcoded URLs, timeouts, or thresholds
