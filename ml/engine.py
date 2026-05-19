"""
Recommendation engine — public API.

Three top-level flows:
  recommend_home   — hybrid personalised recommendations for a user
  get_trending     — global time-decayed popularity ranking
  search_products  — keyword search re-ranked by hybrid score

To add a new surface (e.g. "Because you bought X"):
  1. Import the algorithm primitives you need from ml/algorithms/
  2. Implement a new function here following the same pattern
  3. Expose it from backend/services/recommendation_service.py
"""

from ml.algorithms.collaborative import build_user_item_matrix, build_cf_scores
from ml.algorithms.content import build_user_signals, content_score
from ml.algorithms.popularity import build_popularity_scores
from ml.algorithms.weights import hybrid_weights


def recommend_home(
    user_id: str,
    users: dict,
    products: dict,
    interactions: list,
    top_n: int = 10,
) -> list:
    """
    Hybrid homepage recommendations for a single user.

    Formula:
      final_score = content_w  * content_score
                  + collab_w   * collab_score_norm
                  + pop_w      * popularity_score_norm

    Falls back to global trending for unknown users.
    Only filters products the user has bought/claimed (not mere views).
    """
    if user_id not in users:
        return get_trending(interactions, products, top_n)

    user = users[user_id]

    popularity = build_popularity_scores(interactions)
    max_pop = max(popularity.values()) if popularity else 1.0

    signals = build_user_signals(user_id, interactions, products)
    interacted = signals["interacted"]
    category_affinity = signals["category_affinity"]
    max_affinity = max(category_affinity.values()) if category_affinity else 1.0

    _EXCLUDE_TYPES = {"buy", "claim", "pay"}
    purchased = {
        e["product_id"]
        for e in interactions
        if e["user_id"] == user_id
        and e["interaction_type"] in _EXCLUDE_TYPES
        and e["product_id"] is not None
    }

    user_item_matrix = build_user_item_matrix(interactions)
    cf_scores = build_cf_scores(user_id, user_item_matrix)
    max_cf = max(cf_scores.values()) if cf_scores else 1.0

    content_w, collab_w, pop_w = hybrid_weights(len(interacted))

    results = []
    for pid, product in products.items():
        if pid in purchased:
            continue
        c_score  = content_score(user, product, category_affinity, max_affinity)
        p_score  = popularity.get(pid, 0.0) / max_pop
        cf_score = cf_scores.get(pid, 0.0) / max_cf
        final    = content_w * c_score + collab_w * cf_score + pop_w * p_score
        results.append((pid, product, final, c_score, cf_score, p_score))

    results.sort(key=lambda x: x[2], reverse=True)

    recommendations = []
    for pid, product, final, c_score, cf_score, p_score in results[:top_n]:
        rec = product.copy()
        rec["final_score"]      = round(final, 4)
        rec["content_score"]    = round(c_score, 4)
        rec["collab_score"]     = round(cf_score, 4)
        rec["popularity_score"] = round(p_score, 4)
        recommendations.append(rec)

    return recommendations


def get_trending(interactions: list, products: dict, top_n: int = 10) -> list:
    """Top-N trending products by global time-decayed interaction score."""
    scores = build_popularity_scores(interactions)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    trending = []
    for pid, score in ranked[:top_n]:
        if pid in products:
            product = products[pid].copy()
            product["popularity_score"] = round(score, 4)
            trending.append(product)
    return trending


def search_products(
    query: str,
    user_id: str,
    users: dict,
    products: dict,
    interactions: list,
    top_n: int = 10,
) -> list:
    """
    Keyword search over product name and category, re-ranked by hybrid score.

    Known users get full hybrid re-ranking; unknown users get pure popularity.
    """
    query_lower = query.lower()
    candidates = [
        p for p in products.values()
        if query_lower in p["name"].lower() or query_lower in p["category"].lower()
    ]

    if not candidates:
        return []

    popularity = build_popularity_scores(interactions)
    max_pop = max(popularity.values()) if popularity else 1.0

    user = users.get(user_id)
    if user:
        signals = build_user_signals(user_id, interactions, products)
        category_affinity = signals["category_affinity"]
        max_affinity = max(category_affinity.values()) if category_affinity else 1.0
        user_item_matrix = build_user_item_matrix(interactions)
        cf_scores = build_cf_scores(user_id, user_item_matrix)
        max_cf = max(cf_scores.values()) if cf_scores else 1.0
        content_w, collab_w, pop_w = hybrid_weights(len(signals["interacted"]))
    else:
        category_affinity, max_affinity = {}, 1.0
        cf_scores, max_cf = {}, 1.0
        content_w, collab_w, pop_w = 0.0, 0.0, 1.0

    results = []
    for product in candidates:
        c_score  = content_score(user, product, category_affinity, max_affinity) if user else 0.0
        p_score  = popularity.get(product["product_id"], 0.0) / max_pop
        cf_score = cf_scores.get(product["product_id"], 0.0) / max_cf
        final    = content_w * c_score + collab_w * cf_score + pop_w * p_score
        results.append((product, final, c_score, cf_score, p_score))

    results.sort(key=lambda x: x[1], reverse=True)

    output = []
    for product, final, c_score, cf_score, p_score in results[:top_n]:
        rec = product.copy()
        rec["final_score"]      = round(final, 4)
        rec["content_score"]    = round(c_score, 4)
        rec["collab_score"]     = round(cf_score, 4)
        rec["popularity_score"] = round(p_score, 4)
        output.append(rec)

    return output
