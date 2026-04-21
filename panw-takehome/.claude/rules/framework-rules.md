# Framework Architecture Rules

## Validators
All validators **must** extend `src.validators.base.BaseValidator` via `required_fields`,
`field_types`, and optionally `custom_checks`. Do not introduce `pydantic` or `jsonschema`.
Rationale: classmethods let validation steps surface naturally in Allure attachments without
coupling the validator to any reporting framework.

## HTTP calls
All HTTP goes through `EnvironmentClient.get` / `EnvironmentClient.post` (or other methods
added later). Never `import requests` in a test file.
Rationale: SLA enforcement (`SLAViolation`) and Allure request-step attachment live inside
the client. Bypassing it silently drops both.

## Environment config
All values that vary per environment (`base_url`, `max_response_time`, `min_results_count`,
`verify_ssl`) live in `config/environments.yaml`. Never add a constant to a Python file that
could vary per environment. Adding a new threshold means: add a field to `EnvironmentConfig`
in `src/config/loader.py` AND populate the YAML. Do not default it in Python if it is
required for correctness.

## Test file placement
| Directory | What belongs here |
|---|---|
| `tests/countries/` | Tests whose assertions are countries-API-specific |
| `tests/weather/` | Tests whose assertions are weather-API-specific |
| `tests/shared/` | Tests that are meaningful for **both** environments |

A file under `tests/countries/` must not reference weather concepts (and vice versa).
Cross-environment tests (e.g., SLA threshold sanity) live in `tests/shared/`.

## Fixtures
`env_client` is session-scoped. Do not instantiate `EnvironmentClient` directly in a test —
you bypass session reuse and teardown. Use the fixture.

## Reporting
Reporters and hooks live in `src/reporting/`. Do not emit Allure steps directly from test
bodies for request-level activity — that is the client's job. Use `allure.step` in tests
only for logical phases ("fetch", "validate", "cross-reference").
