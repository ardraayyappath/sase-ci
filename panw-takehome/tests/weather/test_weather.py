from __future__ import annotations

import json

import allure
import pytest

from conftest import PROJECT_ROOT
from src.clients.env_client import EnvironmentClient
from src.validators.weather import WeatherValidator

_CITIES: list[dict] = json.loads((PROJECT_ROOT / "test_data" / "cities.json").read_text())["cities"]



@pytest.mark.parametrize(
    "city",
    [pytest.param(c, id=c["name"]) for c in _CITIES],
)
def test_city_forecast(env_client: EnvironmentClient, city: dict) -> None:
    with allure.step(f"Fetch forecast for {city['name']}"):
        resp = env_client.get(
            "/forecast",
            params={
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "hourly": "temperature_2m",
            },
        )
    assert resp.status_code == 200
    with allure.step("Validate schema"):
        WeatherValidator.validate(resp.json())
