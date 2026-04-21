"""
Unit tests for EnvironmentClient SLA enforcement.

These tests exercise the client in isolation using mocks — they do NOT hit a real
endpoint and do NOT use the env_client fixture. This is an intentional exception to
the "never instantiate your own client" rule because the subject under test IS the
client mechanism itself, not an API contract.

time.monotonic is controlled via patch so that elapsed time is deterministic.
Tests never call time.monotonic() directly — that would violate framework rules.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.clients.env_client import EnvironmentClient, SLAViolation
from src.config.loader import EnvironmentConfig

_THRESHOLD = 1.0

_CFG = EnvironmentConfig(
    base_url="https://example.com",
    max_response_time=_THRESHOLD,
    min_results_count=1,
    verify_ssl=False,
)


def _make_client() -> EnvironmentClient:
    """Return a client whose session.request is mocked to return HTTP 200."""
    session = MagicMock(spec=requests.Session)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    session.request.return_value = mock_resp
    return EnvironmentClient(name="test-env", config=_CFG, session=session)


# ---------------------------------------------------------------------------
# Boundary: pass cases
# ---------------------------------------------------------------------------

def test_sla_passes_when_under_threshold() -> None:
    """elapsed < threshold — no exception."""
    client = _make_client()
    with patch("src.clients.env_client.time.monotonic", side_effect=[0.0, _THRESHOLD - 0.001]):
        resp = client.get("/fast")
    assert resp.status_code == 200


def test_sla_passes_at_exact_threshold() -> None:
    """elapsed == threshold — boundary value, NOT a violation (operator is strict >)."""
    client = _make_client()
    with patch("src.clients.env_client.time.monotonic", side_effect=[0.0, _THRESHOLD]):
        resp = client.get("/exact")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Boundary: fail cases
# ---------------------------------------------------------------------------

def test_sla_raises_just_over_threshold() -> None:
    """elapsed = threshold + epsilon — smallest violation."""
    client = _make_client()
    with patch("src.clients.env_client.time.monotonic", side_effect=[0.0, _THRESHOLD + 0.001]):
        with pytest.raises(SLAViolation):
            client.get("/slow")


def test_sla_raises_well_over_threshold() -> None:
    """elapsed >> threshold — clear violation."""
    client = _make_client()
    with patch("src.clients.env_client.time.monotonic", side_effect=[0.0, _THRESHOLD * 3]):
        with pytest.raises(SLAViolation):
            client.get("/very-slow")


# ---------------------------------------------------------------------------
# Exception contract
# ---------------------------------------------------------------------------

def test_sla_violation_is_assertion_error() -> None:
    """SLAViolation must subclass AssertionError so pytest marks it FAILED not ERROR."""
    assert issubclass(SLAViolation, AssertionError)


def test_sla_violation_message_contains_context() -> None:
    """Exception message must include env name, path, elapsed time, and threshold."""
    elapsed = _THRESHOLD + 0.5
    client = _make_client()
    with patch("src.clients.env_client.time.monotonic", side_effect=[0.0, elapsed]):
        with pytest.raises(SLAViolation) as exc_info:
            client.get("/slow-endpoint")

    msg = str(exc_info.value)
    assert "test-env" in msg          # env name
    assert "/slow-endpoint" in msg    # path
    assert f"{elapsed:.3f}" in msg    # elapsed (formatted as in the client)
    assert str(_THRESHOLD) in msg     # threshold
