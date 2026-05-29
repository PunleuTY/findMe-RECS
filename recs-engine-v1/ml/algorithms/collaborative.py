"""User-based collaborative filtering."""

import math
from collections import defaultdict

from ml.config import INTERACTION_WEIGHTS, CF_TOP_K_NEIGHBOURS
from ml.algorithms.time_decay import time_decay


def build_user_item_matrix(interactions: list) -> dict:
    """Sparse user-item matrix: {user_id: {product_id: decayed_score}}."""
    matrix: dict = defaultdict(lambda: defaultdict(float))
    for event in interactions:
        if event["product_id"] is None:
            continue
        weight = INTERACTION_WEIGHTS.get(event["interaction_type"], 1)
        matrix[event["user_id"]][event["product_id"]] += weight * time_decay(event["timestamp"])
    return {uid: dict(items) for uid, items in matrix.items()}


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two sparse product-score vectors."""
    common = set(vec_a) & set(vec_b)
    if not common:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def build_cf_scores(
    user_id: str,
    user_item_matrix: dict,
    top_k: int = CF_TOP_K_NEIGHBOURS,
) -> dict:
    """
    User-based CF: top-K cosine-similar neighbours → similarity-weighted
    aggregate item scores. Returns {product_id: cf_score}.
    """
    if user_id not in user_item_matrix:
        return {}
    user_vec = user_item_matrix[user_id]
    neighbours = [
        (cosine_similarity(user_vec, other_vec), other_vec)
        for other_id, other_vec in user_item_matrix.items()
        if other_id != user_id
    ]
    neighbours = [(sim, vec) for sim, vec in neighbours if sim > 0]
    if not neighbours:
        return {}
    neighbours.sort(key=lambda x: x[0], reverse=True)
    top_neighbours = neighbours[:top_k]

    product_scores: dict = defaultdict(float)
    product_sim_sum: dict = defaultdict(float)
    for sim, other_vec in top_neighbours:
        for pid, score in other_vec.items():
            product_scores[pid] += sim * score
            product_sim_sum[pid] += sim
    return {pid: product_scores[pid] / product_sim_sum[pid] for pid in product_scores}
