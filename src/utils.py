"""Shared helpers for file IO, caching, and reproducibility."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

RANDOM_SEED = 42


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def seed_everything(seed: int = RANDOM_SEED) -> None:
    import random

    random.seed(seed)
    np.random.seed(seed)


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)
