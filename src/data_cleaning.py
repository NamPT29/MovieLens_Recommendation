"""Data cleaning routines for the MovieLens project."""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with reasonable defaults."""
    df = df.copy()
    for column in df.columns:
        if df[column].dtype == "O":
            df[column] = df[column].fillna("unknown")
        else:
            df[column] = df[column].fillna(df[column].median())
    return df


def remove_duplicates(df: pd.DataFrame, subset: Tuple[str, ...]) -> pd.DataFrame:
    return df.drop_duplicates(subset=list(subset))


def winsorize_counts(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    return series.clip(lower=lower_bound, upper=upper_bound)


def build_master_frame(raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    ratings = raw_data["ratings"].copy()
    movies = raw_data["movies"].copy()
    tags = raw_data["tags"].copy()

    ratings = remove_duplicates(ratings, ("userId", "movieId", "timestamp"))
    movies = handle_missing_values(movies)
    tags = handle_missing_values(tags)

    tag_agg = (
        tags.groupby("movieId")["tag"].apply(lambda x: " ".join(sorted(set(str(t).lower() for t in x))))
    ).reset_index(name="tag_text")

    df = ratings.merge(movies, on="movieId", how="left")
    df = df.merge(tag_agg, on="movieId", how="left")

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["year"] = df["title"].str.extract(r"(\(\d{4}\))").replace({np.nan: ""})
    df["year"] = df["year"].str.extract(r"(\d{4})").astype(float)

    movie_stats = df.groupby("movieId")["rating"].agg(["mean", "count", "std"]).reset_index()
    movie_stats = movie_stats.rename(columns={"mean": "avg_rating", "count": "rating_count", "std": "rating_std"})
    movie_stats["rating_std"] = movie_stats["rating_std"].fillna(0.0)
    movie_stats["rating_count"] = winsorize_counts(movie_stats["rating_count"])

    df = df.merge(movie_stats, on="movieId", how="left")
    df["tag_text"] = df["tag_text"].fillna("")
    df["genres"] = df["genres"].replace({"(no genres listed)": ""})
    df["genres"] = df["genres"].fillna("")
    df["genre_list"] = df["genres"].str.split("|")
    df["clean_title"] = df["title"].str.replace(r"(\s*\(\d{4}\))", "", regex=True)

    return df
