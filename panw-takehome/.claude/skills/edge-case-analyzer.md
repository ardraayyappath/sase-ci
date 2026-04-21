# Skill: edge-case-analyzer

Identify realistic edge cases for an endpoint in the panw-takehome framework.
Separates high-signal cases from speculative ones before any test is written.

## Inputs
- `endpoint_path` — e.g. `/region/{name}`, `/forecast`
- `http_method` — GET | POST
- `response_shape` — brief description of top-level fields
- `known_invariants` — domain rules already encoded (e.g. in `CountryValidator`, `WeatherValidator`)

## Output

Edge cases grouped into four categories, each with a label and a recommendation:

| Label | Meaning |
|-------|---------|
| `high-value` | Durable, catches real API regressions — implement |
| `optional` | Useful but not critical — implement if time allows |
| `likely hallucinated` | No public evidence this failure mode exists — skip |
| `already covered` | Existing validator or test handles it — note and move on |

For each case, state:
- What the condition is
- Why it matters (or doesn't)
- Whether to automate it in this framework

## Framework constraints

| Rule | Implication |
|------|-------------|
| Tests public third-party APIs | Cannot inject failures; must use real-world boundary values |
| SLA enforced by `EnvironmentClient._request` | No need to suggest response-time edge cases |
| Schema validated by `BaseValidator` subclasses | Suggest validator additions, not inline assertions |
| Parametrize data from `test_data/*.json` | Edge cases that need data go in JSON files |
| `env_client.config.min_results_count` gates empty-result assertions | Use it, not a hardcoded `0` |

## Categories to always check

1. **Schema** — missing fields, wrong types, null values in arrays
2. **Domain boundary** — empty lists, zero counts, extreme coordinates, mismatched array lengths
3. **Invalid input** — bad param type, unknown resource name, empty string
4. **SLA** — already covered by `EnvironmentClient`; mark any suggestion here as redundant
5. **Volatile data** — exact counts, specific country names, current temperatures — mark as `likely hallucinated`

## Anti-patterns to reject

- Suggesting exact-value assertions on live API data (e.g. "assert London temperature == 12°C")
- Concurrent / load testing against a public free API
- Internal failure modes with no public evidence (e.g. "API returns duplicate cca3")
- Snapshot assertions on full response bodies

## Example output format

```
### Schema edge cases

| Case | Label | Automate? |
|------|-------|-----------|
| temperature_2m contains null | high-value | Yes — add null guard in WeatherValidator.custom_checks |
| time[] and temperature_2m[] length mismatch | high-value | Yes — assert len(temps) == len(times) |
| timezone missing from response | already covered | WeatherValidator.required_fields |

### Domain boundary cases

| Case | Label | Automate? |
|------|-------|-----------|
| len(hourly.time) >= 24 | high-value | Yes — durable lower bound, not fragile exact count |
| Coordinates snap to grid (response != request) | optional | No — don't assert exact match |

### Likely hallucinated

| Case | Why skip |
|------|----------|
| API returns 429 rate limit | No published rate limit; public free API |
| temperature exactly == -80.0 | Real atmosphere never produces exact boundary |
```
