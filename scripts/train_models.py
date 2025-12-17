"""Run the full pipeline: clean data, generate features, train models, save artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from src import data_cleaning, data_ingestion
from src.features import FeatureStore, build_user_item_matrix
from src.recommender import ContentBasedRecommender, MatrixFactorizationRecommender, persist_models
from src.utils import ensure_dir, seed_everything


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MovieLens recommenders")
    parser.add_argument("--raw_dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed_dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--artifact_dir", type=Path, default=Path("models/artifacts"))
    args = parser.parse_args()

    seed_everything()
    ensure_dir(args.processed_dir)
    ensure_dir(args.artifact_dir)

    raw_data = data_ingestion.load_raw_data(args.raw_dir)
    master_df = data_cleaning.build_master_frame(raw_data)
    processed_path = args.processed_dir / "master.parquet"
    master_df.to_parquet(processed_path, index=False)

    item_df = master_df.drop_duplicates("movieId")[
        ["movieId", "clean_title", "genres", "tag_text", "avg_rating", "rating_count", "rating_std", "year"]
    ].reset_index(drop=True)

    feature_store = FeatureStore()
    feature_matrix = feature_store.build_item_features(item_df)
    content_model = ContentBasedRecommender(item_df=item_df, feature_store=feature_store, feature_matrix=feature_matrix)

    ratings_df = master_df[["userId", "movieId", "rating"]]
    collab_model = MatrixFactorizationRecommender.train(ratings_df)

    persist_models(content_model, collab_model, feature_store, args.artifact_dir)
    joblib.dump(item_df, args.artifact_dir / "item_df.joblib")

    ratings, user_item = build_user_item_matrix(master_df)
    joblib.dump(ratings, args.artifact_dir / "ratings.joblib")
    joblib.dump(user_item, args.artifact_dir / "user_item.joblib")

    print("Training complete. Artifacts saved to", args.artifact_dir.resolve())


if __name__ == "__main__":
    main()
