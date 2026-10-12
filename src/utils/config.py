from __future__ import annotations
import os
from pathlib import Path
import yaml


def load_yaml(path: str | Path) -> dict:
    """Load a YAML configuration file."""
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable."""
    return os.getenv(name, default)
