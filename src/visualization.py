"""Visualization utilities for the exploratory analysis requirements."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def plot_rating_distribution(ratings: pd.DataFrame, output: Optional[Path] = None):
    plt.figure(figsize=(8, 4))
    sns.histplot(ratings["rating"], bins=20, kde=True, color="#1f77b4")
    plt.title("Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    _save_or_show(output)


def plot_top_genres(df: pd.DataFrame, top_n: int = 10, output: Optional[Path] = None):
    genre_counts = df["genre_list"].explode().value_counts().head(top_n)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=genre_counts.values, y=genre_counts.index, palette="viridis")
    plt.title("Top Genres by Frequency")
    plt.xlabel("Count")
    _save_or_show(output)


def plot_top_movies_by_ratings(df: pd.DataFrame, min_count: int = 100, output: Optional[Path] = None):
    filtered = df[df["rating_count"] >= min_count]
    agg = filtered.groupby("clean_title")["avg_rating"].mean().sort_values(ascending=False).head(15)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=agg.values, y=agg.index, palette="mako")
    plt.title("Top Movies (avg rating >= min count)")
    plt.xlabel("Average Rating")
    _save_or_show(output)


def plot_rating_heatmap(df: pd.DataFrame, output: Optional[Path] = None):
    pivot = df.pivot_table(index="userId", columns="movieId", values="rating").fillna(0)
    sample = pivot.sample(n=min(30, pivot.shape[0]), random_state=42)
    plt.figure(figsize=(10, 6))
    sns.heatmap(sample, cmap="rocket_r", cbar=True)
    plt.title("User-Movie Rating Heatmap (sample)")
    _save_or_show(output)


def _save_or_show(output: Optional[Path]):
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output, dpi=150)
        plt.close()
    else:
        plt.tight_layout()
        plt.show()
