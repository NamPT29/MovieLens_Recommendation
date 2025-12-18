"""Analytics and data processing functions."""

from .profile import describe_user_profile, genre_counts
from .charts import (
    build_insight_figures,
    build_catalogue_figures,
    build_usage_timeline,
    build_additional_figures,
)

__all__ = [
    "describe_user_profile",
    "genre_counts",
    "build_insight_figures",
    "build_catalogue_figures",
    "build_usage_timeline",
    "build_additional_figures",
]
