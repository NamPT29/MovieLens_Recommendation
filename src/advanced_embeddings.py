"""Advanced embeddings using sentence transformers."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class AdvancedEmbeddingRecommender:
    """Content-based recommender using BERT-based embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model.
        
        Args:
            model_name: HuggingFace model name. Options:
                - 'all-MiniLM-L6-v2' (fast, 384 dim)
                - 'all-mpnet-base-v2' (better quality, 768 dim)
        """
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.item_df = None
    
    def fit(self, item_df: pd.DataFrame) -> AdvancedEmbeddingRecommender:
        """Generate embeddings for all movies.
        
        Args:
            item_df: DataFrame with movieId, clean_title, genres, tag_text
        """
        self.item_df = item_df.copy()
        
        # Combine text features
        texts = []
        for _, row in item_df.iterrows():
            text = f"{row.get('clean_title', '')} "
            text += f"{row.get('genres', '').replace('|', ' ')} "
            text += f"{row.get('tag_text', '')}"
            texts.append(text.strip())
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} movies...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        return self
    
    def recommend(
        self,
        user_history: pd.DataFrame,
        top_k: int = 10,
        diversity_factor: float = 0.3
    ) -> pd.DataFrame:
        """Generate recommendations based on user's watch history.
        
        Args:
            user_history: DataFrame with userId, movieId, rating
            top_k: Number of recommendations
            diversity_factor: 0-1, higher means more diverse results
        """
        if self.embeddings is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Get user's watched movies
        watched_ids = set(user_history["movieId"].unique())
        watched_indices = self.item_df[
            self.item_df["movieId"].isin(watched_ids)
        ].index.tolist()
        
        if not watched_indices:
            # Cold start: return popular items
            return self.item_df.nlargest(top_k, "rating_count")[
                ["movieId", "clean_title", "genres", "avg_rating", "rating_count"]
            ]
        
        # Compute average embedding of watched movies (weighted by rating)
        watched_embeddings = self.embeddings[watched_indices]
        ratings = user_history.set_index("movieId").loc[
            self.item_df.iloc[watched_indices]["movieId"]
        ]["rating"].values
        
        # Normalize ratings to weights
        weights = (ratings - ratings.min()) / (ratings.max() - ratings.min() + 1e-8)
        user_profile = np.average(watched_embeddings, axis=0, weights=weights)
        
        # Compute similarity to all items
        similarities = cosine_similarity([user_profile], self.embeddings)[0]
        
        # Filter out watched movies
        candidate_mask = ~self.item_df["movieId"].isin(watched_ids)
        candidate_indices = self.item_df[candidate_mask].index
        candidate_scores = similarities[candidate_indices]
        
        # Apply diversity penalty (MMR-like)
        if diversity_factor > 0:
            selected = []
            remaining = set(range(len(candidate_indices)))
            
            while len(selected) < top_k and remaining:
                if not selected:
                    # First item: highest similarity
                    idx = np.argmax(candidate_scores)
                    selected.append(candidate_indices[idx])
                    remaining.remove(idx)
                else:
                    # Balance similarity and diversity
                    scores = []
                    selected_embeddings = self.embeddings[selected]
                    
                    for idx in remaining:
                        sim_to_user = candidate_scores[idx]
                        emb = self.embeddings[candidate_indices[idx]]
                        max_sim_to_selected = cosine_similarity(
                            [emb], selected_embeddings
                        )[0].max()
                        
                        # MMR score
                        score = (
                            (1 - diversity_factor) * sim_to_user
                            - diversity_factor * max_sim_to_selected
                        )
                        scores.append((idx, score))
                    
                    best_idx, _ = max(scores, key=lambda x: x[1])
                    selected.append(candidate_indices[best_idx])
                    remaining.remove(best_idx)
            
            top_indices = selected
        else:
            # Standard ranking
            top_indices = candidate_indices[np.argsort(-candidate_scores)[:top_k]]
        
        recommendations = self.item_df.iloc[top_indices].copy()
        recommendations["model_score"] = similarities[top_indices]
        
        return recommendations[
            ["movieId", "clean_title", "genres", "avg_rating", "rating_count", "model_score"]
        ]
    
    def get_similar_items(self, movie_id: int, top_k: int = 10) -> pd.DataFrame:
        """Find similar movies to a given movie."""
        if self.embeddings is None:
            raise ValueError("Model not fitted.")
        
        idx = self.item_df[self.item_df["movieId"] == movie_id].index[0]
        movie_emb = self.embeddings[idx]
        
        similarities = cosine_similarity([movie_emb], self.embeddings)[0]
        top_indices = np.argsort(-similarities)[1:top_k+1]  # Skip self
        
        results = self.item_df.iloc[top_indices].copy()
        results["similarity"] = similarities[top_indices]
        
        return results[["movieId", "clean_title", "genres", "similarity"]]
