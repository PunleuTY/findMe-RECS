"""MySQL connection helpers. Uses PyMySQL with DictCursor so callers get plain dicts."""

from contextlib import contextmanager
from typing import Any, Iterable

import pymysql
import pymysql.cursors

from backend.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def _connect() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


@contextmanager
def get_connection():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: Iterable[Any] = ()) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_one(sql: str, params: Iterable[Any] = ()) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def execute(sql: str, params: Iterable[Any] = ()) -> int:
    """Run INSERT/UPDATE/DELETE, commit, and return lastrowid or rowcount."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            new_id = cur.lastrowid or cur.rowcount
            conn.commit()
            return new_id
