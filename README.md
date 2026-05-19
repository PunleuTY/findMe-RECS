# FindMe RS — Hybrid Product Recommendation System

A production-ready recommendation engine combining **content-based filtering**, **collaborative filtering**, and **time-decayed popularity scoring** into a single hybrid model.

Built with a **FastAPI** Python backend and a **Next.js 14 + Tailwind CSS** frontend.

---

## Features

| Surface | Algorithm |
|---|---|
| Homepage feed | Hybrid: content × CF × popularity (adaptive weights) |
| Trending | Global time-decayed popularity (7-day half-life) |
| Product detail | Same-category popularity-ranked similar items |
| Search | Keyword filter → hybrid re-ranking for known users |
| Event logging | Real-time view/lead/buy tracking persisted to MySQL |

### Hybrid weight schedule

```
cold-start (0 interactions): content=0.30, collab=0.10, popularity=0.60
warm user  (25+ interactions): content=0.50, collab=0.18, popularity=0.32
```

Weights grow linearly and are capped — ensuring popular items surface for new users while personalisation takes over as history accumulates.

---

## Project Structure

```
findMe-RS-repo/
├── backend/                 ← FastAPI Python service
│   ├── main.py              ← App factory + router registration
│   ├── config.py            ← DB + API settings (from .env)
│   ├── requirements.txt
│   ├── api/                 ← Route handlers
│   │   ├── recommendations.py
│   │   ├── products.py
│   │   ├── categories.py
│   │   ├── search.py
│   │   ├── events.py
│   │   ├── users.py
│   │   └── schemas.py
│   ├── database/
│   │   ├── connection.py    ← PyMySQL helpers (fetch_all, fetch_one, execute)
│   │   ├── queries.py       ← Read-side SQL (products, categories, users)
│   │   ├── events.py        ← Write-side SQL (view, lead, buy, search logs)
│   │   └── schema.sql       ← MySQL DDL (14 tables)
│   └── services/
│       └── recommendation_service.py  ← Thread-safe singleton + TTL cache
│
├── ml/                      ← Algorithm modules (pure Python, no DB)
│   ├── config.py            ← Algorithm constants (single source of truth)
│   ├── engine.py            ← Orchestration: recommend_home, get_trending, search_products
│   ├── data_loader.py       ← MySQL → (users, products, interactions) tuple
│   └── algorithms/
│       ├── time_decay.py    ← exp(-λ·days) decay shared by all scorers
│       ├── popularity.py    ← Global time-decayed popularity scores
│       ├── collaborative.py ← User-item matrix + cosine CF
│       ├── content.py       ← User signals + content score blending
│       └── weights.py       ← Adaptive content/collab/pop weight schedule
│
├── tests/
│   ├── conftest.py          ← In-memory fixtures (no DB required)
│   └── ml/
│       └── test_recommender.py  ← 30 unit tests for all algorithm modules
│
├── frontend/                ← Next.js 14 + Tailwind storefront
│   ├── src/app/             ← Pages: home, trending, categories, search, product detail
│   ├── src/components/      ← Header, ProductCard, ProductGrid, UserPicker, SectionHeading
│   └── src/lib/             ← api.ts, types.ts, format.ts, session.ts, tracker.ts
│
├── data/generated/          ← Runtime JSON (gitignored; populated by data_loader)
├── .env.example
└── pyproject.toml
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8+ (or MariaDB 10.5+)

### 1. Database setup

```bash
# Create database and tables
mysql -u root -p < backend/database/schema.sql
```

Populate with your data or connect to your existing MySQL instance.

### 2. Backend

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DB credentials

# Start the API server
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

The storefront will be available at `http://localhost:3000`.

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/recommendations/home/{user_id}` | Personalised homepage feed |
| `GET` | `/api/recommendations/trending` | Global trending products |
| `POST` | `/api/recommendations/refresh` | Force reload from MySQL |
| `GET` | `/api/products` | Product listing (filterable by category/page_type) |
| `GET` | `/api/products/{id}` | Product detail + similar items |
| `GET` | `/api/categories` | All categories |
| `GET` | `/api/categories/{id}` | Category detail + products |
| `GET` | `/api/search?q=...` | Keyword search with hybrid re-ranking |
| `GET` | `/api/users` | User listing |
| `GET` | `/api/users/{id}` | User profile + interaction history |
| `POST` | `/api/events` | Log view/lead/buy interaction |
| `GET` | `/api/health` | Health check |

Query params: `top_n` (1–50), `limit`, `offset`, `category_id`, `page_type`, `user_id`.

---

## Running Tests

```bash
source .venv/bin/activate
pytest -v
```

All 30 tests run in memory — no database or network required.

```
tests/ml/test_recommender.py  — time decay, CF, popularity, content, weights, engine
```

---

## Configuration

All algorithm constants live in `ml/config.py`. Tune them here only:

| Constant | Default | Effect |
|---|---|---|
| `TIME_DECAY_HALF_LIFE_DAYS` | 7 | Older interactions decay faster |
| `CF_TOP_K_NEIGHBOURS` | 10 | Number of similar users for CF |
| `COLD_CONTENT_BASE` | 0.30 | Content weight for new users |
| `COLD_COLLAB_BASE` | 0.10 | CF weight for new users |
| `MAX_CONTENT_WEIGHT` | 0.50 | Content weight cap |
| `MAX_COLLAB_WEIGHT` | 0.25 | CF weight cap |

---

## Extending the System

| Goal | Where to change |
|---|---|
| New scoring signal | Add `ml/algorithms/<signal>.py`, import in `ml/engine.py` |
| New recommendation surface | Add function in `ml/engine.py`, expose in `RecommendationService` |
| Tune constants | Edit `ml/config.py` only |
| Different database | Replace `ml/data_loader.py:load_data()` |
| New API endpoint | Add route file in `backend/api/`, register in `backend/main.py` |

---

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for hosting guides (Railway, Render, VPS).

---

## Tech Stack

**Backend:** Python 3.11 · FastAPI · PyMySQL · Pydantic v2 · Uvicorn  
**ML:** Pure Python (no ML framework dependencies)  
**Frontend:** Next.js 14 (App Router) · TypeScript · Tailwind CSS  
**Database:** MySQL 8+ / MariaDB 10.5+
