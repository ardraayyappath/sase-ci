from __future__ import annotations

import allure
import pytest


@pytest.fixture(autouse=True)
def _allure_env_tag(request: pytest.FixtureRequest) -> None:
    """Tag every test with its environment epic and feature for Allure grouping."""
    env_name: str | None = None
    if "env_name" in request.fixturenames:
        env_name = request.getfixturevalue("env_name")
    if env_name:
        allure.dynamic.epic(f"env:{env_name}")
    allure.dynamic.feature(request.node.parent.name if request.node.parent else "root")
