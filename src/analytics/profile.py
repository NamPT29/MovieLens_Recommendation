"""User profile analysis functions."""

import pandas as pd


def describe_user_profile(user_history: pd.DataFrame, item_df: pd.DataFrame) -> dict[str, str]:
    """Generate user profile statistics."""
    if user_history.empty:
        return {"count": "0", "avg": "-", "genres": "Chưa có dữ liệu"}
    avg_rating = round(float(user_history["rating"].mean()), 2)
    merged = user_history.merge(item_df[["movieId", "genres"]], on="movieId", how="left")
    genres = merged["genres"].dropna().str.split("|").explode()
    top_genres = ", ".join(genres.value_counts().head(2).index.tolist()) if not genres.empty else "-"
    return {
        "count": f"{len(user_history):,}",
        "avg": f"{avg_rating:.2f}",
        "genres": top_genres or "-",
    }


def genre_counts(source: pd.DataFrame, item_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate genre frequency counts."""
    if source.empty:
        return pd.DataFrame(columns=["genre", "count"])
    merged = source.merge(item_df[["movieId", "genres"]], on="movieId", how="left")
    exploded = merged["genres"].dropna().str.split("|").explode()
    counts = exploded.value_counts().head(8).reset_index()
    counts.columns = ["genre", "count"]
    return counts
