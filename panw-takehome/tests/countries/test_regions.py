from __future__ import annotations

import json

import allure
import pytest

from conftest import PROJECT_ROOT
from src.clients.env_client import EnvironmentClient
from src.validators.region_country import RegionCountryValidator

_DATA = json.loads((PROJECT_ROOT / "test_data" / "regions.json").read_text())
_REGIONS = _DATA["regions"]
_INVALID_REGIONS = _DATA["invalid_regions"]


@pytest.mark.parametrize(
    "region",
    [pytest.param(r, id=r["name"]) for r in _REGIONS],
)
def test_region_returns_sufficient_countries(
    env_client: EnvironmentClient, region: dict
) -> None:
    with allure.step(f"Fetch /region/{region['name']}"):
        resp = env_client.get(f"/region/{region['name']}")
    assert resp.status_code == 200
    countries = resp.json()
    with allure.step("Assert result count meets minimum"):
        assert len(countries) >= env_client.config.min_results_count
    with allure.step("Assert region-specific country count"):
        assert len(countries) >= region["min_countries"], (
            f"Expected >= {region['min_countries']} countries in {region['name']}, "
            f"got {len(countries)}"
        )


@pytest.mark.parametrize(
    "region",
    [pytest.param(r, id=r["name"]) for r in _REGIONS],
)
def test_region_schema(env_client: EnvironmentClient, region: dict) -> None:
    with allure.step(f"Fetch /region/{region['name']}"):
        resp = env_client.get(f"/region/{region['name']}")
    assert resp.status_code == 200
    with allure.step("Validate schema of first entry"):
        RegionCountryValidator.validate(resp.json()[0])


@pytest.mark.negative
@pytest.mark.parametrize(
    "bad_region",
    [pytest.param(r, id=r["description"]) for r in _INVALID_REGIONS],
)
def test_region_rejects_invalid(
    env_client: EnvironmentClient, bad_region: dict
) -> None:
    with allure.step(f"Fetch /region/{bad_region['name']!r} (expect error)"):
        resp = env_client.get(f"/region/{bad_region['name']}")
    assert resp.status_code >= 400, (
        f"Expected 4xx for invalid region '{bad_region['name']}', "
        f"got {resp.status_code}"
    )
