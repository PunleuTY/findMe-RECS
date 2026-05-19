"""
FastAPI entrypoint.

Run from project root:
    source .venv/bin/activate
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import categories, events, products, recommendations, search, users
from backend.config import CORS_ORIGINS


def create_app() -> FastAPI:
    app = FastAPI(
        title="FindMe RS API",
        version="1.0.0",
        description="Hybrid recommendation engine: content + collaborative filtering + popularity.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products.router)
    app.include_router(categories.router)
    app.include_router(recommendations.router)
    app.include_router(search.router)
    app.include_router(events.router)
    app.include_router(users.router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
