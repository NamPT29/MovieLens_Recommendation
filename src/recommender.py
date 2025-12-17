"""Recommendation models: content-based, collaborative, and hybrid."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD

from .features import FeatureStore


@dataclass
class ContentBasedRecommender:
    item_df: pd.DataFrame
    feature_store: FeatureStore
    feature_matrix: np.ndarray

    def __post_init__(self) -> None:
        self.item_df = self.item_df.reset_index(drop=True)
        self.movie_index = {mid: idx for idx, mid in enumerate(self.item_df["movieId"])}

    def _build_user_profile(self, user_history: pd.DataFrame) -> np.ndarray:
        if user_history.empty:
            return self.feature_matrix.mean(axis=0)

        top_history = user_history.sort_values("rating", ascending=False).head(20)
        rows = [self.movie_index[mid] for mid in top_history["movieId"] if mid in self.movie_index]
        if not rows:
            return self.feature_matrix.mean(axis=0)
        liked_matrix = self.feature_matrix[rows]
        weights = top_history.loc[top_history["movieId"].isin(self.movie_index)].sort_values("rating", ascending=False)["rating"].values.reshape(-1, 1)
        return (liked_matrix * weights).sum(axis=0)

    def recommend(self, user_history: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        user_profile = self._build_user_profile(user_history)
        scores = self.feature_matrix @ user_profile

        recommendations = self.item_df.copy()
        recommendations["score"] = scores
        seen_ids = set(user_history["movieId"].unique())
        recommendations = recommendations[~recommendations["movieId"].isin(seen_ids)]
        fallback_score = (
            0.7 * recommendations["avg_rating"].fillna(recommendations["avg_rating"].median())
            + 0.3 * recommendations["rating_count"].fillna(recommendations["rating_count"].median())
        )
        recommendations["score"] = recommendations["score"].fillna(fallback_score)
        return recommendations.sort_values("score", ascending=False).head(top_k)


@dataclass
class MatrixFactorizationRecommender:
    user_factors: np.ndarray
    item_factors: np.ndarray
    user_index: Dict[int, int]
    item_index: Dict[int, int]
    ratings: pd.DataFrame
    global_mean: float

    @classmethod
    def train(cls, ratings: pd.DataFrame, n_factors: int = 50) -> "MatrixFactorizationRecommender":
        user_ids = sorted(ratings["userId"].unique())
        item_ids = sorted(ratings["movieId"].unique())
        user_index = {uid: idx for idx, uid in enumerate(user_ids)}
        item_index = {iid: idx for idx, iid in enumerate(item_ids)}

        matrix = np.zeros((len(user_ids), len(item_ids)), dtype=np.float32)
        for row in ratings.itertuples():
            matrix[user_index[row.userId], item_index[row.movieId]] = row.rating

        max_rank = max(2, min(len(user_ids), len(item_ids)) - 1)
        n_components = min(n_factors, max_rank)
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        user_factors = svd.fit_transform(matrix)
        item_factors = svd.components_.T

        return cls(
            user_factors=user_factors,
            item_factors=item_factors,
            user_index=user_index,
            item_index=item_index,
            ratings=ratings,
            global_mean=float(ratings["rating"].mean()),
        )

    def _scores_for_user(self, user_id: int) -> np.ndarray:
        if user_id not in self.user_index:
            return np.full(len(self.item_index), self.global_mean, dtype=float)
        user_vec = self.user_factors[self.user_index[user_id]]
        return user_vec @ self.item_factors.T

    def predict_for_user(self, user_id: int, candidate_ids: List[int]) -> pd.DataFrame:
        scores = self._scores_for_user(user_id)
        pred = []
        for movie_id in candidate_ids:
            idx = self.item_index.get(movie_id)
            if idx is None:
                pred.append(self.global_mean)
            else:
                pred.append(scores[idx])
        return pd.DataFrame({"movieId": candidate_ids, "est_rating": pred})

    def recommend(self, user_id: int, item_df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        seen = set(self.ratings.loc[self.ratings["userId"] == user_id, "movieId"].unique())
        candidates = [mid for mid in item_df["movieId"].tolist() if mid not in seen]
        pred_df = self.predict_for_user(user_id, candidates)
        recs = item_df.merge(pred_df, on="movieId")
        return recs.sort_values("est_rating", ascending=False).head(top_k)


@dataclass
class HybridRecommender:
    content_model: ContentBasedRecommender
    collab_model: MatrixFactorizationRecommender
    alpha: float = 0.5

    def recommend(self, user_id: int, user_history: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        content_recs = self.content_model.recommend(user_history, top_k=200)
        collab_recs = self.collab_model.recommend(user_id, self.content_model.item_df, top_k=200)

        merged = content_recs.merge(collab_recs[["movieId", "est_rating"]], on="movieId", how="outer", suffixes=("_content", "_collab"))
        merged["score_content"] = merged["score"].fillna(merged["score"].median())
        merged["score_collab"] = merged["est_rating"].fillna(merged["est_rating"].median())
        merged["hybrid_score"] = self.alpha * merged["score_content"] + (1 - self.alpha) * merged["score_collab"]
        return merged.sort_values("hybrid_score", ascending=False).head(top_k)


def persist_models(
    content_model: ContentBasedRecommender,
    collab_model: MatrixFactorizationRecommender,
    feature_store: FeatureStore,
    artifact_dir: Path,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(content_model, artifact_dir / "content_model.joblib")
    joblib.dump(collab_model, artifact_dir / "svd_model.joblib")
    joblib.dump(feature_store, artifact_dir / "feature_store.joblib")


def load_models(artifact_dir: Path):
    content_model = joblib.load(artifact_dir / "content_model.joblib")
    collab_model = joblib.load(artifact_dir / "svd_model.joblib")
    feature_store = joblib.load(artifact_dir / "feature_store.joblib")
    return content_model, collab_model, feature_store
