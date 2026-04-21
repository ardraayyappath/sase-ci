from __future__ import annotations

from src.clients.env_client import EnvironmentClient


def test_base_url_reachable(env_client: EnvironmentClient) -> None:
    # Empty path hits base_url directly (e.g. https://restcountries.com/v3.1).
    # Routed through env_client.get so SLA enforcement and Allure attachment apply.
    # Any response < 500 means the server is up; 404 is acceptable here.
    resp = env_client.get("")
    assert resp.status_code < 500


def test_sla_threshold_configured(env_client: EnvironmentClient) -> None:
    assert env_client.config.max_response_time > 0
    assert env_client.config.min_results_count >= 1
