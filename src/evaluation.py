"""Evaluation helpers for rating prediction and ranking quality."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def rmse(y_true, y_pred) -> float:
    # Some sklearn builds omit the `squared` argument, so compute square root manually.
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mae(y_true, y_pred) -> float:
    return mean_absolute_error(y_true, y_pred)


def precision_at_k(recommendations: Dict[int, List[int]], ground_truth: Dict[int, List[int]], k: int = 10) -> float:
    precisions = []
    for user, preds in recommendations.items():
        if not preds:
            continue
        relevant = set(ground_truth.get(user, []))
        hit_count = len(set(preds[:k]) & relevant)
        precisions.append(hit_count / min(k, len(preds)))
    return float(np.mean(precisions)) if precisions else 0.0


def recall_at_k(recommendations: Dict[int, List[int]], ground_truth: Dict[int, List[int]], k: int = 10) -> float:
    recalls = []
    for user, preds in recommendations.items():
        relevant = set(ground_truth.get(user, []))
        if not relevant:
            continue
        hit_count = len(set(preds[:k]) & relevant)
        recalls.append(hit_count / len(relevant))
    return float(np.mean(recalls)) if recalls else 0.0
