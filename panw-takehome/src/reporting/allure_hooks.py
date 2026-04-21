from __future__ import annotations

import allure


def tag_allure_env(request: object) -> None:
    """Apply Allure epic/feature tags based on the env_name fixture value.

    Accepts a pytest.FixtureRequest but does not import pytest, keeping
    src/ free of test-framework dependencies.
    """
    env_name: str | None = None
    if "env_name" in request.fixturenames:  # type: ignore[attr-defined]
        env_name = request.getfixturevalue("env_name")  # type: ignore[attr-defined]
    if env_name:
        allure.dynamic.epic(f"env:{env_name}")
    parent = request.node.parent  # type: ignore[attr-defined]
    allure.dynamic.feature(parent.name if parent else "root")
