"""Global time-decayed popularity scoring."""

from collections import defaultdict

from ml.config import INTERACTION_WEIGHTS
from ml.algorithms.time_decay import time_decay


def build_popularity_scores(interactions: list) -> dict:
    """
    Global time-decayed popularity score per product.

    Returns {product_id: score}. Visit events (product_id=None) are skipped.
    """
    scores: dict = defaultdict(float)
    for event in interactions:
        if event["product_id"] is None:
            continue
        weight = INTERACTION_WEIGHTS.get(event["interaction_type"], 1)
        scores[event["product_id"]] += weight * time_decay(event["timestamp"])
    return dict(scores)
