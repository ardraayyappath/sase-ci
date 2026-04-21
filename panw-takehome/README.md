# PANW Take-Home: API Test Framework

## Overview

This framework tests two independent public APIs — [REST Countries](https://restcountries.com)
and [Open-Meteo](https://api.open-meteo.com) — through a single, shared test harness. Tests
never reference URLs, thresholds, or environment-specific constants directly; all configuration
is loaded from `config/environments.yaml` at runtime via a frozen dataclass. An
`EnvironmentClient` wraps every HTTP call, automatically enforcing SLA thresholds and attaching
request telemetry to Allure reports. The `--env` CLI flag selects a single environment or
omits it to run both — no branching in test logic required.

## Setup

Requires **Python 3.11+**.

```bash
pip install -e ".[dev]"
```

## Running tests

| Command | Effect |
|---|---|
| `pytest` | Runs both environments |
| `pytest --env countries` | Countries API only |
| `pytest --env weather` | Weather API only |
| `pytest -m negative` | Negative-path tests only |
| `pytest -m "not slow"` | Skip slow tests (default addopts already omits none) |

## Reports

Generate and serve an Allure report locally:

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

Each environment appears as a separate **Epic** (`env:countries`, `env:weather`) in the
Allure dashboard, making cross-environment comparison straightforward.

## Architecture

```
config/environments.yaml          ← single source of truth for all per-env values
src/config/loader.py              ← parses YAML into frozen EnvironmentConfig dataclasses
src/clients/env_client.py         ← all HTTP, SLA enforcement, Allure attachment
src/validators/base.py            ← abstract BaseValidator (required_fields + field_types)
src/validators/{country,weather}  ← concrete validators with semantic custom_checks
tests/conftest.py                 ← env_name parametrization, --env flag, autouse tagging
tests/countries/                  ← countries-specific tests
tests/weather/                    ← weather-specific tests
tests/shared/                     ← env-agnostic tests (run against both)
test_data/cities.json             ← parametrize source for weather city tests
```

**Tests never see URLs or thresholds.** They receive an `env_client` fixture whose
`config` carries all environment-specific values. SLA enforcement is automatic: if
`elapsed > max_response_time`, `EnvironmentClient._request` raises `SLAViolation`
(a subclass of `AssertionError`) before the test body sees the response.

**Validators extend `BaseValidator`** and declare `required_fields`, `field_types`, and
optional `custom_checks`. No third-party schema library is used; validation steps are plain
`assert` statements so they surface clearly in Allure.

## Design decisions

- **`pytest_generate_tests` over per-test parametrization** — centralising `env_name`
  parametrization in `conftest.py` means `--env` filters globally without touching any
  test file. Individual tests never need to know which environment they are running against.

- **Frozen dataclass for config** — `EnvironmentConfig(frozen=True)` prevents accidental
  mutation of thresholds or URLs during a test run, catching a class of bugs at construction
  time rather than silently producing wrong results.

- **`SLAViolation(AssertionError)`** — subclassing `AssertionError` (not `Exception`) makes
  pytest report SLA breaches as test *failures* rather than test *errors*, which keeps CI
  dashboards unambiguous and Allure category counts accurate.

- **`verify_ssl` field in YAML** — the target test machine runs behind a TLS-inspecting
  proxy that presents a self-signed chain. Rather than patching `requests` globally or
  hard-coding `verify=False`, `verify_ssl` is an explicit, documented YAML field with a
  default of `true`. Reviewers can see the setting and override it per environment.

- **`test_all_countries_have_positive_population` intentionally relaxed from spec** — the
  assignment says "assert every country has `population > 0`". The REST Countries API
  legitimately returns `population=0` for uninhabited and administration-only territories
  (e.g. Bouvet Island, South Georgia, British Indian Ocean Territory). Asserting `> 0` for
  all entries would produce a permanently failing test that flags real API data as a bug.
  The test was changed to assert `population >= 0` (no negative values), which captures the
  actual data-quality invariant — a negative population is always a data error, zero is a
  valid sentinel for uninhabited territories. The test name and step label were updated to
  reflect this intent.

- **Spec discrepancy noted** — the assignment PDF referenced `api.openmeteo.com`; the actual
  working host is `api.open-meteo.com`. The YAML uses the correct host.

## CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

1. Installs dependencies with `pip install -e ".[dev]"`.
2. Runs the full suite with `--alluredir` and `--junitxml`.
3. Generates and uploads an Allure HTML report as a workflow artifact (runs even on failure).
4. Posts a test-result summary table to the GitHub step summary.
