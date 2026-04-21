from __future__ import annotations

from src.clients.env_client import EnvironmentClient


def test_base_url_reachable(env_client: EnvironmentClient) -> None:
    resp = env_client.session.get(
        env_client.config.base_url,
        timeout=5,
        verify=env_client.config.verify_ssl,
    )
    assert resp.status_code < 500


def test_sla_threshold_configured(env_client: EnvironmentClient) -> None:
    assert env_client.config.max_response_time > 0
    assert env_client.config.min_results_count >= 1
