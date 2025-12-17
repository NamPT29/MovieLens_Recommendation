"""TMDB helper utilities: map MovieLens IDs to TMDB posters."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import os

import pandas as pd
import requests
import streamlit as st

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
LINKS_PATH = Path("data/raw/ml-latest-small/links.csv")


def _get_api_key() -> Optional[str]:
    """Return TMDB API key from Streamlit secrets or environment.

    The user must set TMDB_API_KEY in .streamlit/secrets.toml (recommended)
    or as an environment variable.
    """

    # Prefer Streamlit secrets on Streamlit Cloud
    if "TMDB_API_KEY" in st.secrets:
        key = str(st.secrets["TMDB_API_KEY"]).strip()
        if key:
            return key

    # Fallback to environment variable
    key = os.getenv("TMDB_API_KEY", "").strip()
    return key or None


@lru_cache(maxsize=1)
def _load_links() -> pd.DataFrame:
    """Load MovieLens links.csv to map movieId -> tmdbId.

    Returns an empty DataFrame if the file is missing so callers can
    fail gracefully without crashing the app.
    """

    if not LINKS_PATH.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(LINKS_PATH)
        # Ensure required columns exist
        expected_cols = {"movieId", "tmdbId"}
        if not expected_cols.issubset(df.columns):
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@lru_cache(maxsize=2048)
def get_poster_url(movie_id: int) -> Optional[str]:
    """Return a TMDB poster URL for a given MovieLens movieId.

    - Looks up tmdbId from links.csv
    - Calls TMDB /movie/{tmdb_id} API
    - Builds a full image URL from poster_path
    - Returns None on any error (network, missing mapping, etc.)
    """

    api_key = _get_api_key()
    if not api_key:
        return None

    links_df = _load_links()
    if links_df.empty:
        return None

    try:
        row = links_df.loc[links_df["movieId"] == int(movie_id)].iloc[0]
    except Exception:
        return None

    tmdb_id = row.get("tmdbId")
    try:
        tmdb_id_int = int(tmdb_id)
    except Exception:
        return None

    url = f"{TMDB_API_BASE}/movie/{tmdb_id_int}"
    try:
        resp = requests.get(url, params={"api_key": api_key}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    poster_path = data.get("poster_path")
    if not poster_path:
        return None

    return f"{TMDB_IMAGE_BASE}{poster_path}"