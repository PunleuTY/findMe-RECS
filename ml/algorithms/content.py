"""Content-based scoring algorithms."""

from collections import defaultdict

from ml.config import INTERACTION_WEIGHTS
from ml.algorithms.time_decay import time_decay


def build_user_signals(user_id: str, interactions: list, products: dict) -> dict:
    """
    Single-pass extraction of user signals from interaction history.

    Returns:
      interacted        — set of product IDs the user has touched
      category_affinity — time-decayed weighted score per category
    """
    interacted: set = set()
    category_affinity: dict[str, float] = defaultdict(float)

    for event in interactions:
        if event["user_id"] != user_id or event["product_id"] is None:
            continue
        pid = event["product_id"]
        interacted.add(pid)
        product = products.get(pid)
        if product:
            weight = INTERACTION_WEIGHTS.get(event["interaction_type"], 1)
            category_affinity[product["category"]] += weight * time_decay(event["timestamp"])

    return {"interacted": interacted, "category_affinity": dict(category_affinity)}


def content_score(
    user: dict,
    product: dict,
    category_affinity: dict,
    max_affinity: float,
) -> float:
    """
    Blended content relevance score in [0, 1].

      0.5 from preference  — static preferred_categories OR learned from interactions
      0.5 from affinity    — normalized time-decayed interaction score for the category
    """
    category = product["category"]
    static_pref  = category in user.get("preferred_categories", [])
    learned_pref = category in category_affinity
    pref_score   = 0.5 if (static_pref or learned_pref) else 0.0

    raw_aff   = category_affinity.get(category, 0.0)
    aff_score = 0.5 * (raw_aff / max_affinity) if max_affinity > 0 else 0.0
    return pref_score + aff_score
