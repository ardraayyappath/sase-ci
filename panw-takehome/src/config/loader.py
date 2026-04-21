from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

# Anchor so resolution works regardless of cwd
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class EnvironmentConfig:
    base_url: str
    max_response_time: float
    min_results_count: int
    verify_ssl: bool = True


def load_environments(
    path: Path = Path("config/environments.yaml"),
) -> dict[str, EnvironmentConfig]:
    resolved = path if path.is_absolute() else _PROJECT_ROOT / path
    with resolved.open() as fh:
        raw: dict = yaml.safe_load(fh)
    return {
        name: EnvironmentConfig(**values)
        for name, values in raw["environments"].items()
    }
