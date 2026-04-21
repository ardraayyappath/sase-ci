from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.weather import WeatherValidator

_CITIES_PATH = Path(__file__).resolve().parents[2] / "test_data" / "cities.json"
_CITIES: list[dict] = json.loads(_CITIES_PATH.read_text())["cities"]



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
