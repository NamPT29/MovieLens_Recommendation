"""Context-aware recommendation considering time, recency, and trends."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


class ContextAwareRecommender:
    """Recommendations that adapt to context (time, trends, recency)."""
    
    def __init__(self, base_recommender):
        """Initialize with a base recommender (content/collab/hybrid)."""
        self.base_recommender = base_recommender
    
    def recommend(
        self,
        user_history: pd.DataFrame,
        user_id: int,
        top_k: int = 10,
        time_of_day: Optional[str] = None,
        recency_weight: float = 0.2,
        trending_weight: float = 0.1,
    ) -> pd.DataFrame:
        """Generate context-aware recommendations.
        
        Args:
            user_history: User's rating history
            user_id: User ID
            top_k: Number of recommendations
            time_of_day: 'morning', 'afternoon', 'evening', 'night' or None (auto-detect)
            recency_weight: Weight for recent popularity (0-1)
            trending_weight: Weight for trending items (0-1)
        """
        # Get base recommendations
        base_recs = self.base_recommender.recommend(user_history, top_k=top_k * 2)
        
        if "model_score" not in base_recs.columns:
            base_recs["model_score"] = base_recs.get("score", 0.5)
        
        # Normalize base scores
        base_recs["base_score_norm"] = (
            (base_recs["model_score"] - base_recs["model_score"].min())
            / (base_recs["model_score"].max() - base_recs["model_score"].min() + 1e-8)
        )
        
        # 1. Time-of-day context
        if time_of_day is None:
            time_of_day = self._detect_time_of_day()
        
        base_recs["time_boost"] = base_recs.apply(
            lambda row: self._time_preference_boost(row["genres"], time_of_day),
            axis=1
        )
        
        # 2. Recency boost (recently popular)
        if "timestamp" in user_history.columns:
            base_recs["recency_score"] = self._compute_recency_score(
                base_recs, user_history
            )
        else:
            base_recs["recency_score"] = 0
        
        # 3. Trending boost
        base_recs["trending_score"] = self._compute_trending_score(user_history)
        
        # 4. Sequential patterns (what users watch next)
        base_recs["sequential_boost"] = self._sequential_boost(
            base_recs, user_history
        )
        
        # Combine scores
        base_recs["context_score"] = (
            (1 - recency_weight - trending_weight) * base_recs["base_score_norm"]
            + recency_weight * base_recs["recency_score"]
            + trending_weight * base_recs["trending_score"]
            + base_recs["time_boost"] * 0.1
            + base_recs["sequential_boost"] * 0.1
        )
        
        # Re-rank and return top K
        recommendations = base_recs.nlargest(top_k, "context_score")
        recommendations["model_score"] = recommendations["context_score"]
        
        return recommendations[
            ["movieId", "clean_title", "genres", "avg_rating", "rating_count", "model_score"]
        ]
    
    @staticmethod
    def _detect_time_of_day() -> str:
        """Auto-detect current time of day."""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def _time_preference_boost(genres: str, time_of_day: str) -> float:
        """Boost score based on genre-time correlation.
        
        Based on common viewing patterns:
        - Morning: Documentary, Family
        - Afternoon: Action, Adventure
        - Evening: Drama, Romance, Comedy
        - Night: Horror, Thriller, Sci-Fi
        """
        if not isinstance(genres, str):
            return 0.0
        
        genres_lower = genres.lower()
        
        preferences = {
            "morning": ["documentary", "family", "animation", "children"],
            "afternoon": ["action", "adventure", "comedy"],
            "evening": ["drama", "romance", "comedy", "musical"],
            "night": ["horror", "thriller", "mystery", "sci-fi", "fantasy"]
        }
        
        boost = 0.0
        for pref_genre in preferences.get(time_of_day, []):
            if pref_genre in genres_lower:
                boost += 0.1
        
        return min(boost, 0.5)  # Cap at 0.5
    
    @staticmethod
    def _compute_recency_score(
        recommendations: pd.DataFrame,
        user_history: pd.DataFrame
    ) -> pd.Series:
        """Score based on recent popularity among similar users."""
        if "timestamp" not in user_history.columns:
            return pd.Series(0, index=recommendations.index)
        
        # Recent = last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        recent_ratings = user_history[
            pd.to_datetime(user_history["timestamp"]) >= cutoff
        ]
        
        if recent_ratings.empty:
            return pd.Series(0, index=recommendations.index)
        
        # Count recent ratings for each movie
        recent_counts = recent_ratings.groupby("movieId").size()
        
        scores = []
        for movie_id in recommendations["movieId"]:
            count = recent_counts.get(movie_id, 0)
            scores.append(count)
        
        # Normalize
        scores = np.array(scores)
        if scores.max() > 0:
            scores = scores / scores.max()
        
        return pd.Series(scores, index=recommendations.index)
    
    @staticmethod
    def _compute_trending_score(user_history: pd.DataFrame) -> float:
        """Placeholder for trending score (would need global data)."""
        # In production, compute velocity: (recent_views - older_views) / time
        return 0.0
    
    @staticmethod
    def _sequential_boost(
        recommendations: pd.DataFrame,
        user_history: pd.DataFrame
    ) -> pd.Series:
        """Boost items commonly watched after user's recent movies."""
        if user_history.empty:
            return pd.Series(0, index=recommendations.index)
        
        # Get user's last 3 movies
        recent = user_history.nlargest(3, "timestamp")
        recent_genres = set()
        
        for _, row in recent.iterrows():
            if isinstance(row.get("genres"), str):
                recent_genres.update(row["genres"].split("|"))
        
        # Boost movies sharing genres with recent watches
        scores = []
        for _, rec in recommendations.iterrows():
            if not isinstance(rec.get("genres"), str):
                scores.append(0)
                continue
            
            rec_genres = set(rec["genres"].split("|"))
            overlap = len(rec_genres & recent_genres)
            scores.append(overlap * 0.1)
        
        return pd.Series(scores, index=recommendations.index)
