"""Data ingestion utilities for MovieLens."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

RAW_FILENAMES = {
    "ratings": "ml-latest-small/ratings.csv",
    "movies": "ml-latest-small/movies.csv",
    "tags": "ml-latest-small/tags.csv",
    "links": "ml-latest-small/links.csv",
}


def load_raw_data(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    data = {}
    for key, filename in RAW_FILENAMES.items():
        file_path = raw_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Missing raw file: {file_path}")
        data[key] = pd.read_csv(file_path)
    return data
