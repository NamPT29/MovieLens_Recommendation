"""Feature engineering for recommendation models."""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler


class FeatureStore:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english", min_df=2)
        self.scaler = MinMaxScaler()

    def build_item_features(self, df: pd.DataFrame):
        df = df.copy()
        df["text_blob"] = (
            df["clean_title"].fillna("")
            + " "
            + df["genres"].str.replace("|", " ", regex=False).fillna("")
            + " "
            + df["tag_text"].fillna("")
        )
        tfidf_matrix = self.vectorizer.fit_transform(df["text_blob"])

        stats = df[["avg_rating", "rating_count", "rating_std"]].fillna(0)
        scaled_stats = self.scaler.fit_transform(stats)
        dense_features = np.hstack([tfidf_matrix.toarray(), scaled_stats])
        return dense_features

    def transform_item_features(self, df: pd.DataFrame):
        df = df.copy()
        df["text_blob"] = (
            df["clean_title"].fillna("")
            + " "
            + df["genres"].str.replace("|", " ", regex=False).fillna("")
            + " "
            + df["tag_text"].fillna("")
        )
        tfidf_matrix = self.vectorizer.transform(df["text_blob"])
        stats = df[["avg_rating", "rating_count", "rating_std"]].fillna(0)
        scaled_stats = self.scaler.transform(stats)
        dense_features = np.hstack([tfidf_matrix.toarray(), scaled_stats])
        return dense_features


def build_user_item_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ratings = df[["userId", "movieId", "rating"]].drop_duplicates()
    user_item = ratings.pivot_table(index="userId", columns="movieId", values="rating")
    return ratings, user_item
