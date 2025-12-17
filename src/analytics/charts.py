"""Chart generation functions for analytics."""

from datetime import timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from .profile import genre_counts


def build_insight_figures(
    user_history: pd.DataFrame, item_df: pd.DataFrame, ratings: pd.DataFrame
) -> tuple[Figure, Figure, str, str]:
    """Build rating distribution and genre charts."""
    if len(user_history) >= 2:
        rating_source = user_history
        rating_label = "Phân bố rating của người dùng"
    else:
        rating_source = ratings.sample(min(len(ratings), 5000), random_state=42)
        rating_label = "Phân bố rating toàn bộ tập"

    fig_rating = px.histogram(
        rating_source,
        x="rating",
        nbins=10,
        labels={"rating": "Điểm"},
        color_discrete_sequence=["#ff6b35"],
    )
    fig_rating.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    genre_data = genre_counts(user_history, item_df)
    if genre_data.empty:
        genre_data = genre_counts(ratings, item_df)
        genre_label = "Top thể loại toàn bộ tập"
    else:
        genre_label = "Thể loại nổi bật của người dùng"

    fig_genre = px.bar(
        genre_data,
        x="count",
        y="genre",
        orientation="h",
        labels={"count": "Số lần", "genre": "Thể loại"},
        color_discrete_sequence=["#8aa1ff"],
    )
    fig_genre.update_layout(
        margin=dict(l=70, r=20, t=10, b=10),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(categoryorder="total ascending"),
    )

    return fig_rating, fig_genre, rating_label, genre_label


def build_catalogue_figures(ratings: pd.DataFrame, item_df: pd.DataFrame) -> tuple[Figure, Figure, str, str]:
    """Build catalogue popularity and rating correlation charts."""
    agg = (
        ratings.groupby("movieId")["rating"].agg(["count", "mean"]).reset_index()
        .rename(columns={"count": "rating_count", "mean": "avg_rating"})
        .merge(item_df[["movieId", "clean_title", "genres"]], on="movieId", how="left")
    )

    top_popular = agg.sort_values("rating_count", ascending=False).head(8)
    scatter_source = agg[agg["rating_count"] >= 10].copy()
    if scatter_source.empty:
        scatter_source = agg.copy()
    if len(scatter_source) > 400:
        scatter_source = scatter_source.nlargest(400, "rating_count")

    pop_fig = px.bar(
        top_popular,
        x="rating_count",
        y="clean_title",
        orientation="h",
        labels={"rating_count": "Số lượt", "clean_title": "Phim"},
        color_discrete_sequence=["#ffd166"],
    )
    pop_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=120, r=20, t=10, b=10),
        yaxis=dict(categoryorder="total ascending"),
    )

    scatter_fig = px.scatter(
        scatter_source,
        x="rating_count",
        y="avg_rating",
        size="avg_rating",
        color="avg_rating",
        hover_data={"clean_title": True, "genres": True},
        color_continuous_scale="Sunset",
        labels={"rating_count": "Số lượt", "avg_rating": "Điểm trung bình"},
    )
    scatter_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
    )

    return pop_fig, scatter_fig, "Top phim được đánh giá nhiều nhất", "Mối quan hệ lượt đánh giá vs. điểm"


def build_usage_timeline(logs: list[dict]) -> tuple[pd.DataFrame, Figure | None]:
    """Build timeline visualization of user interactions."""
    if not logs:
        return pd.DataFrame(), None

    timeline_df = pd.DataFrame(logs)
    if timeline_df.empty:
        return timeline_df, None

    if "created_at" in timeline_df:
        timeline_df["created_at"] = pd.to_datetime(timeline_df["created_at"])
    else:
        timeline_df["created_at"] = pd.to_datetime(timeline_df.index)

    timeline_df.sort_values("created_at", inplace=True)
    timeline_df["end_at"] = timeline_df["created_at"] + timedelta(minutes=2)

    def _field(name: str, fallback: str = "-") -> pd.Series:
        series = timeline_df.get(name)
        if series is None:
            return pd.Series([fallback] * len(timeline_df), index=timeline_df.index)
        return series.fillna(fallback).astype(str)

    timeline_df["hover"] = (
        "User #" + timeline_df["user_id"].astype(str)
        + " · Model: " + _field("model_used", "?")
        + "<br>Movie: " + _field("movie_id")
        + "<br>Score: " + _field("score_shown")
        + "<br>Action: " + _field("action")
    )

    fig = px.timeline(
        timeline_df,
        x_start="created_at",
        x_end="end_at",
        y="user_id",
        color="model_used",
        hover_name="hover",
        labels={"user_id": "User", "model_used": "Model"},
        color_discrete_sequence=["#ff6b35", "#8aa1ff", "#46d4a5", "#f7b955"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=20, t=30, b=20),
        legend_title_text="Thuật toán",
        yaxis=dict(title="User", tickmode="linear"),
        height=320,
    )
    return timeline_df, fig
