from __future__ import annotations

import urllib3
import requests
import pytest

# Suppress InsecureRequestWarning when verify_ssl=false is set in environments.yaml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from pathlib import Path

from src.clients.env_client import EnvironmentClient
from src.config.loader import load_environments
from src.reporting.allure_hooks import _allure_env_tag  # noqa: F401 — registers autouse fixture

# Single authoritative anchor for test data paths — imported by test modules.
PROJECT_ROOT = Path(__file__).resolve().parent


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        choices=["countries", "weather"],
        default=None,
        help="Run tests for a specific environment only (default: both).",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "env_name" not in metafunc.fixturenames:
        return

    selected = metafunc.config.getoption("--env")
    all_envs = list(load_environments().keys())

    # Infer the env scope from the test file's directory so that env-specific
    # tests only ever get one env_name variant — eliminating ghost [other-city]
    # IDs that appear in the report purely to be skipped.
    fspath = str(metafunc.definition.fspath).replace("\\", "/")
    if "/tests/countries/" in fspath:
        file_env: str | None = "countries"
    elif "/tests/weather/" in fspath:
        file_env = "weather"
    else:
        file_env = None  # tests/shared/ or unknown — run against all / selected

    if file_env is not None:
        # Env-specific test: lock to its own env regardless of --env.
        # pytest_collection_modifyitems will skip the item if --env points elsewhere.
        envs = [file_env]
    elif selected:
        envs = [selected]
    else:
        envs = all_envs

    metafunc.parametrize("env_name", envs, scope="session", ids=lambda x: x)


@pytest.fixture(scope="session")
def env_client(env_name: str) -> EnvironmentClient:  # type: ignore[misc]
    envs = load_environments()
    session = requests.Session()
    client = EnvironmentClient(name=env_name, config=envs[env_name], session=session)
    yield client  # type: ignore[misc]
    session.close()



def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    selected = config.getoption("--env")
    if not selected:
        return

    other = "weather" if selected == "countries" else "countries"
    skip_mark = pytest.mark.skip(reason=f"--env={selected}: skipping {other} tests")

    for item in items:
        # tests/shared/ always runs; skip the other env's directory
        if f"tests/{other}/" in item.nodeid.replace("\\", "/"):
            item.add_marker(skip_mark)
