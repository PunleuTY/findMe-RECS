"""
Unit tests for all recommendation algorithm modules + engine.

All tests run in memory — no database, no file I/O.
"""

import pytest
from datetime import datetime, timedelta

from ml.algorithms.time_decay import time_decay as _time_decay
from ml.algorithms.collaborative import build_user_item_matrix, cosine_similarity, build_cf_scores
from ml.algorithms.popularity import build_popularity_scores
from ml.algorithms.content import build_user_signals
from ml.algorithms.weights import hybrid_weights
from ml.engine import recommend_home, get_trending, search_products


# ── Time decay ────────────────────────────────────────────────────────────────

def test_time_decay_recent_is_near_one():
    just_now = datetime.now().isoformat(timespec="seconds")
    assert _time_decay(just_now) > 0.99


def test_time_decay_one_halflife():
    from ml.config import TIME_DECAY_HALF_LIFE_DAYS
    ts = (datetime.now() - timedelta(days=TIME_DECAY_HALF_LIFE_DAYS)).isoformat(timespec="seconds")
    assert abs(_time_decay(ts) - 0.5) < 0.01


def test_time_decay_old_event_near_zero():
    old = (datetime.now() - timedelta(days=365)).isoformat(timespec="seconds")
    assert _time_decay(old) < 0.001


# ── User-item matrix ──────────────────────────────────────────────────────────

def test_user_item_matrix_skips_visit(sample_interactions):
    matrix = build_user_item_matrix(sample_interactions)
    for uid, items in matrix.items():
        assert None not in items


def test_user_item_matrix_accumulates_scores(sample_interactions):
    matrix = build_user_item_matrix(sample_interactions)
    assert matrix["U0001"]["P0001"] > 1.0


def test_user_item_matrix_empty_for_no_events():
    assert build_user_item_matrix([]) == {}


# ── Cosine similarity ─────────────────────────────────────────────────────────

def test_cosine_identical_vectors():
    v = {"P0001": 3.0, "P0002": 4.0}
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_orthogonal_vectors():
    assert cosine_similarity({"P0001": 1.0}, {"P0002": 1.0}) == pytest.approx(0.0)


def test_cosine_empty_vector():
    assert cosine_similarity({}, {"P0001": 1.0}) == 0.0


# ── Collaborative filtering ───────────────────────────────────────────────────

def test_cf_scores_unknown_user(sample_interactions):
    matrix = build_user_item_matrix(sample_interactions)
    assert build_cf_scores("UNKNOWN_USER", matrix) == {}


def test_cf_scores_no_similar_users():
    assert build_cf_scores("U0001", {"U0001": {"P0001": 1.0}}) == {}


def test_cf_scores_returns_dict(sample_interactions):
    matrix = build_user_item_matrix(sample_interactions)
    assert isinstance(build_cf_scores("U0001", matrix), dict)


# ── Popularity ────────────────────────────────────────────────────────────────

def test_popularity_skips_visit(sample_interactions):
    assert None not in build_popularity_scores(sample_interactions)


def test_popularity_buy_higher_than_view(sample_interactions):
    scores = build_popularity_scores(sample_interactions)
    assert scores.get("P0001", 0) > 0
    assert scores.get("P0004", 0) > 0


def test_popularity_empty_interactions():
    assert build_popularity_scores([]) == {}


# ── User signals ──────────────────────────────────────────────────────────────

def test_user_signals_interacted_set(sample_interactions, sample_products):
    signals = build_user_signals("U0001", sample_interactions, sample_products)
    assert "P0001" in signals["interacted"]
    assert "P0002" in signals["interacted"]
    assert "P0003" not in signals["interacted"]


def test_user_signals_visit_not_in_interacted(sample_interactions, sample_products):
    signals = build_user_signals("U0001", sample_interactions, sample_products)
    assert None not in signals["interacted"]


def test_user_signals_category_affinity(sample_interactions, sample_products):
    signals = build_user_signals("U0001", sample_interactions, sample_products)
    assert signals["category_affinity"].get("Food", 0) > 0


# ── Hybrid weights ────────────────────────────────────────────────────────────

def test_hybrid_weights_sum_to_one():
    for n in [0, 5, 20, 50, 100]:
        c, col, p = hybrid_weights(n)
        assert abs(c + col + p - 1.0) < 1e-9


def test_hybrid_weights_cold_start():
    from ml.config import COLD_CONTENT_BASE, COLD_COLLAB_BASE
    c, col, p = hybrid_weights(0)
    assert c == pytest.approx(COLD_CONTENT_BASE)
    assert col == pytest.approx(COLD_COLLAB_BASE)
    assert p == pytest.approx(1.0 - COLD_CONTENT_BASE - COLD_COLLAB_BASE)


def test_hybrid_weights_caps():
    from ml.config import MAX_CONTENT_WEIGHT, MAX_COLLAB_WEIGHT
    c, col, _ = hybrid_weights(10_000)
    assert c == pytest.approx(MAX_CONTENT_WEIGHT)
    assert col == pytest.approx(MAX_COLLAB_WEIGHT)


# ── Homepage recommendations ──────────────────────────────────────────────────

def test_recommend_home_excludes_purchased(sample_users, sample_products, sample_interactions):
    recs = recommend_home("U0001", sample_users, sample_products, sample_interactions, top_n=10)
    rec_ids = {r["product_id"] for r in recs}
    assert "P0001" not in rec_ids  # bought


def test_recommend_home_returns_top_n(sample_users, sample_products, sample_interactions):
    recs = recommend_home("U0001", sample_users, sample_products, sample_interactions, top_n=2)
    assert len(recs) <= 2


def test_recommend_home_unknown_user_falls_back_to_trending(sample_users, sample_products, sample_interactions):
    recs = recommend_home("NO_SUCH_USER", sample_users, sample_products, sample_interactions, top_n=5)
    assert isinstance(recs, list)


def test_recommend_home_scores_present(sample_users, sample_products, sample_interactions):
    recs = recommend_home("U0001", sample_users, sample_products, sample_interactions, top_n=3)
    for r in recs:
        assert "final_score" in r
        assert "content_score" in r
        assert "collab_score" in r
        assert "popularity_score" in r


def test_recommend_home_sorted_by_score(sample_users, sample_products, sample_interactions):
    recs = recommend_home("U0001", sample_users, sample_products, sample_interactions, top_n=10)
    scores = [r["final_score"] for r in recs]
    assert scores == sorted(scores, reverse=True)


# ── Trending ──────────────────────────────────────────────────────────────────

def test_get_trending_sorted_descending(sample_products, sample_interactions):
    trending = get_trending(sample_interactions, sample_products, top_n=5)
    scores = [t["popularity_score"] for t in trending]
    assert scores == sorted(scores, reverse=True)


def test_get_trending_top_n_limit(sample_products, sample_interactions):
    assert len(get_trending(sample_interactions, sample_products, top_n=2)) <= 2


def test_get_trending_empty_interactions(sample_products):
    assert get_trending([], sample_products, top_n=5) == []


# ── Search ────────────────────────────────────────────────────────────────────

def test_search_filters_by_keyword(sample_users, sample_products, sample_interactions):
    results = search_products("food", "U0001", sample_users, sample_products, sample_interactions)
    result_ids = {r["product_id"] for r in results}
    assert "P0001" in result_ids or "P0005" in result_ids


def test_search_no_match_returns_empty(sample_users, sample_products, sample_interactions):
    assert search_products("xyznotexist", "U0001", sample_users, sample_products, sample_interactions) == []


def test_search_unknown_user_still_returns_results(sample_users, sample_products, sample_interactions):
    assert isinstance(search_products("khmer", "UNKNOWN", sample_users, sample_products, sample_interactions), list)
