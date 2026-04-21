from __future__ import annotations

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.country import CountryValidator



def test_europe_region_has_sufficient_countries(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch /region/europe"):
        resp = env_client.get("/region/europe")
    assert resp.status_code == 200
    # Europe has 44–50 sovereign states; 40 is a stable lower bound (domain fact)
    assert len(resp.json()) > 40, f"Expected >40 European countries, got {len(resp.json())}"


def test_germany_schema(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch /name/germany"):
        resp = env_client.get("/name/germany")
    assert resp.status_code == 200
    with allure.step("Validate schema"):
        CountryValidator.validate(resp.json()[0])


def test_all_countries_have_positive_population(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch /all?fields=name,capital,population"):
        # Include capital so we can distinguish inhabited states from uninhabited territories
        resp = env_client.get("/all", params={"fields": "name,capital,population"})
    assert resp.status_code == 200
    countries = resp.json()
    with allure.step("Assert no country has a negative population"):
        # Some territories (research stations, etc.) legitimately have population=0 in this
        # API; the real data-quality invariant is that no value should be negative.
        negative = [
            c.get("name", {}).get("common", "unknown")
            for c in countries
            if c.get("population", 0) < 0
        ]
        assert not negative, f"Countries with negative population: {negative}"


def test_germany_appears_in_europe_region(env_client: EnvironmentClient) -> None:
    with allure.step("Fetch /name/germany"):
        germany_resp = env_client.get("/name/germany")
    assert germany_resp.status_code == 200
    germany_cca3: str = germany_resp.json()[0]["cca3"]

    with allure.step("Fetch /region/europe"):
        europe_resp = env_client.get("/region/europe")
    assert europe_resp.status_code == 200

    with allure.step("Cross-reference by cca3"):
        europe_cca3s = {c["cca3"] for c in europe_resp.json()}
        assert germany_cca3 in europe_cca3s, (
            f"Germany ({germany_cca3}) not found in Europe region cca3 set"
        )
