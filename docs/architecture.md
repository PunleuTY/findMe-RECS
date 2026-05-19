# Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Next.js Frontend (port 3000)                                       │
│  pages: home / trending / categories / search / product detail      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  HTTP (fetch)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI Backend (port 8000)                                        │
│  backend/api/  ← route handlers                                     │
│  backend/services/recommendation_service.py  ← singleton + cache   │
└────────────┬──────────────────────────────────────────┬────────────┘
             │  load_data()                             │  queries.py / events.py
             ▼                                          ▼
┌────────────────────────┐              ┌───────────────────────────┐
│  ml/engine.py          │              │  MySQL (findme_rs_db)     │
│  ml/algorithms/*.py    │              │  14 tables                │
│  (pure Python, no DB)  │              │  schema.sql               │
└────────────────────────┘              └───────────────────────────┘
```

## Data flow (homepage recommendations)

1. `GET /api/recommendations/home/{user_id}` hits `backend/api/recommendations.py`
2. Route calls `RecommendationService.recommend_home(user_id)`
3. Service checks TTL cache — if stale, calls `ml/data_loader.load_data()` (MySQL)
4. `ml/engine.recommend_home()` runs the hybrid pipeline:
   - `build_popularity_scores` → global popularity dict
   - `build_user_signals` → interacted set + category affinity
   - `build_user_item_matrix` + `build_cf_scores` → CF per-product scores
   - `hybrid_weights(n_interacted)` → adaptive (content_w, collab_w, pop_w)
   - Per product: `final = content_w×c + collab_w×cf + pop_w×pop`
5. Results sorted desc by `final_score`, top N returned as JSON

## Layer responsibilities

| Layer | Owns | Does not own |
|---|---|---|
| `ml/algorithms/` | Scoring math | DB access, HTTP, caching |
| `ml/engine.py` | Algorithm composition | DB, HTTP |
| `ml/data_loader.py` | MySQL → in-memory shape | Scoring |
| `backend/services/` | Cache, TTL, refresh | Scoring math |
| `backend/api/` | HTTP routing, validation | Business logic |
| `backend/database/` | SQL queries | HTTP |
| `frontend/` | UI, event tracking | Server logic |

## Caching strategy

`RecommendationService` holds the full `(users, products, interactions)` dataset in memory. It refreshes from MySQL when:
- More than `RECS_CACHE_TTL_SECONDS` (default 300s) have elapsed, OR
- `POST /api/recommendations/refresh` is called

This means recommendations are eventually consistent — interactions logged via `POST /api/events` will be reflected in the next cache refresh cycle.

## Interaction signal table union

The `_load_interactions()` query in `ml/data_loader.py` unions four tables:

| Table | Signal | Weight |
|---|---|---|
| `crm_product_views` | view | 1 |
| `benefit_me_reach_products` | view (aggregated) | 1 |
| `benefit_me_engagements` | view / lead / buy | 1 / 4 / 8 |
| `crm_benefit_more_info_archives` | view / lead / buy | 1 / 4 / 8 |
