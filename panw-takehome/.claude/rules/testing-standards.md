# Testing Standards

## Parametrize from JSON
Parametrize test data from JSON files in `test_data/`. Do not inline literal data in
`@pytest.mark.parametrize`. Example of what **not** to do:
```python
@pytest.mark.parametrize("city", ["London", "Tokyo"])   # WRONG
```
Correct:
```python
_CITIES = json.loads((PROJECT_ROOT / "test_data/cities.json").read_text())["cities"]

@pytest.mark.parametrize("city", [pytest.param(c, id=c["name"]) for c in _CITIES])
```

## Required coverage per endpoint
Every endpoint under test requires:
1. A **positive-path test** asserting HTTP 200 and at least `min_results_count` results.
2. A **schema validation test** using a `BaseValidator` subclass.
3. An **SLA check** — automatic via `EnvironmentClient` (no manual assertion needed).

## Markers
- Negative tests: `@pytest.mark.negative`
- Positive tests: unmarked
- Tests that may legitimately exceed SLA in slow environments: `@pytest.mark.slow`

## Allure steps in tests
Use `allure.step` only for **logical phases** within a test ("fetch", "validate",
"cross-reference"). Request-level steps (`[env] GET /path`) are emitted by the client.

## Readable parametrize IDs
Always pass `id=` (or `ids=`) to parametrized tests so Allure shows human-readable names,
not auto-generated `param0`, `param1`.

## No manual SLA assertions
Never assert on `elapsed` or call `time.time()` / `time.monotonic()` in a test. The client
raises `SLAViolation(AssertionError)` automatically and it surfaces as a test failure.
