"""Backend configuration — loads from .env at project root, then falls back to env vars."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_NAME     = os.getenv("DB_NAME", "findme_rs_db")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

RECS_CACHE_TTL_SECONDS = int(os.getenv("RECS_CACHE_TTL_SECONDS", "300"))
DEFAULT_TOP_N          = int(os.getenv("DEFAULT_TOP_N", "12"))
