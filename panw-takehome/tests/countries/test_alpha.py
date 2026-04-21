from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.alpha_country import AlphaCountryValidator

_DATA = json.loads(
    (Path(__file__).resolve().parents[2] / "test_data" / "country_codes.json").read_text()
)
_VALID_CODES = _DATA["valid_codes"]
_INVALID_CODES = _DATA["invalid_codes"]


@pytest.mark.parametrize(
    "code_entry",
    [pytest.param(c, id=c["description"]) for c in _VALID_CODES],
)
def test_alpha_code_returns_country(
    env_client: EnvironmentClient, code_entry: dict
) -> None:
    with allure.step(f"Fetch /alpha/{code_entry['code']}"):
        resp = env_client.get(f"/alpha/{code_entry['code']}")
    assert resp.status_code == 200, (
        f"Expected 200 for code {code_entry['code']!r}, got {resp.status_code}"
    )
    with allure.step("Validate schema of first result"):
        results = resp.json()
        AlphaCountryValidator.validate(results[0])


@pytest.mark.parametrize(
    "code_entry",
    [pytest.param(c, id=c["description"]) for c in _VALID_CODES],
)
def test_alpha_code_returns_at_least_one_result(
    env_client: EnvironmentClient, code_entry: dict
) -> None:
    with allure.step(f"Fetch /alpha/{code_entry['code']}"):
        resp = env_client.get(f"/alpha/{code_entry['code']}")
    assert resp.status_code == 200, (
        f"Expected 200 for code {code_entry['code']!r}, got {resp.status_code}"
    )
    with allure.step("Assert result count meets minimum"):
        results = resp.json()
        assert len(results) >= env_client.config.min_results_count, (
            f"Expected >= {env_client.config.min_results_count} results for "
            f"code {code_entry['code']!r}, got {len(results)}"
        )


@pytest.mark.negative
@pytest.mark.parametrize(
    "bad_code",
    [pytest.param(c, id=c["description"]) for c in _INVALID_CODES],
)
def test_alpha_rejects_invalid_code(
    env_client: EnvironmentClient, bad_code: dict
) -> None:
    with allure.step(f"Fetch /alpha/{bad_code['code']!r} (expect error)"):
        resp = env_client.get(f"/alpha/{bad_code['code']}")
    assert resp.status_code >= 400, (
        f"Expected 4xx for invalid code {bad_code['code']!r}, got {resp.status_code}"
    )
