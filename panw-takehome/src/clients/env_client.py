from __future__ import annotations

import time
from dataclasses import dataclass, field

import allure
import requests

from src.config.loader import EnvironmentConfig


class SLAViolation(AssertionError):
    """Raised when a response exceeds the configured max_response_time threshold."""


@dataclass
class EnvironmentClient:
    name: str
    config: EnvironmentConfig
    session: requests.Session = field(default_factory=requests.Session)

    def _request(self, method: str, path: str, **kwargs: object) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        # SLA fires from our assertion; give the socket extra headroom
        kwargs.setdefault("timeout", self.config.max_response_time + 5)
        kwargs.setdefault("verify", self.config.verify_ssl)

        with allure.step(f"[{self.name}] {method.upper()} {path}"):
            start = time.monotonic()
            resp = self.session.request(method, url, **kwargs)
            elapsed = time.monotonic() - start

        threshold = self.config.max_response_time
        allure.attach(
            f"status={resp.status_code}  elapsed={elapsed:.3f}s  threshold={threshold}s",
            name="request-summary",
            attachment_type=allure.attachment_type.TEXT,
        )

        if elapsed > threshold:
            raise SLAViolation(
                f"[{self.name}] {method.upper()} {path} took {elapsed:.3f}s "
                f"(threshold {threshold}s)"
            )

        return resp

    def get(self, path: str, **kwargs: object) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: object) -> requests.Response:
        return self._request("POST", path, **kwargs)
