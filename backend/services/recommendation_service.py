"""
Thread-safe singleton wrapping the recommendation engine.

Loads data from MySQL once on construction and auto-refreshes after TTL.
Call get_service().refresh() or POST /api/recommendations/refresh to force reload.
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Optional

from ml.engine import recommend_home, get_trending, search_products
from ml.data_loader import load_data
from backend.config import RECS_CACHE_TTL_SECONDS


class RecommendationService:
    def __init__(self, ttl_seconds: int = RECS_CACHE_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._lock = Lock()
        self._loaded_at: float = 0.0
        self.users: dict = {}
        self.products: dict = {}
        self.interactions: list = []
        self.refresh()

    def refresh(self) -> None:
        with self._lock:
            self.users, self.products, self.interactions = load_data()
            self._loaded_at = time.time()

    def _maybe_refresh(self) -> None:
        if time.time() - self._loaded_at > self._ttl:
            self.refresh()

    def recommend_home(self, user_id: str, top_n: int = 10) -> list:
        self._maybe_refresh()
        return recommend_home(user_id, self.users, self.products, self.interactions, top_n=top_n)

    def trending(self, top_n: int = 10) -> list:
        self._maybe_refresh()
        return get_trending(self.interactions, self.products, top_n=top_n)

    def search(self, query: str, user_id: str = "", top_n: int = 10) -> list:
        self._maybe_refresh()
        return search_products(query, user_id, self.users, self.products, self.interactions, top_n=top_n)

    def similar_to(self, product_id: str, top_n: int = 8) -> list:
        """Same-category, popularity-ranked 'similar items'."""
        self._maybe_refresh()
        anchor = self.products.get(str(product_id))
        if anchor is None:
            return []
        from ml.algorithms.popularity import build_popularity_scores

        scores = build_popularity_scores(self.interactions)
        max_pop = max(scores.values()) if scores else 1.0
        rows = [
            (p, scores.get(pid, 0.0) / max_pop)
            for pid, p in self.products.items()
            if pid != str(product_id) and p["category"] == anchor["category"]
        ]
        rows.sort(key=lambda r: r[1], reverse=True)
        out = []
        for p, s in rows[:top_n]:
            rec = p.copy()
            rec["popularity_score"] = round(s, 4)
            out.append(rec)
        return out


_service: Optional[RecommendationService] = None


def get_service() -> RecommendationService:
    global _service
    if _service is None:
        _service = RecommendationService()
    return _service
