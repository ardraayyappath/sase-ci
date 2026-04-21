from __future__ import annotations

import json
from pathlib import Path

import allure
import pytest

from src.clients.env_client import EnvironmentClient
from src.validators.daily_weather import DailyWeatherValidator

_CITIES_PATH = Path(__file__).resolve().parents[2] / "test_data" / "cities.json"
_CITIES: list[dict] = json.loads(_CITIES_PATH.read_text())["cities"]

_INVALID_COORDS = [
    {"latitude": 999, "longitude": 0, "description": "latitude out of range"},
    {"latitude": 0, "longitude": 999, "description": "longitude out of range"},
]


@pytest.mark.parametrize(
    "city",
    [pytest.param(c, id=c["name"]) for c in _CITIES],
)
def test_daily_forecast_schema(env_client: EnvironmentClient, city: dict) -> None:
    with allure.step(f"Fetch daily forecast for {city['name']}"):
        resp = env_client.get(
            "/forecast",
            params={
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min",
            },
        )
    assert resp.status_code == 200
    with allure.step("Validate schema"):
        DailyWeatherValidator.validate(resp.json())


@pytest.mark.negative
@pytest.mark.parametrize(
    "bad",
    [pytest.param(c, id=c["description"]) for c in _INVALID_COORDS],
)
def test_daily_forecast_rejects_invalid_coords(
    env_client: EnvironmentClient, bad: dict
) -> None:
    with allure.step(f"Fetch with invalid coordinates: {bad['description']}"):
        resp = env_client.get(
            "/forecast",
            params={
                "latitude": bad["latitude"],
                "longitude": bad["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min",
            },
        )
    assert resp.status_code >= 400
