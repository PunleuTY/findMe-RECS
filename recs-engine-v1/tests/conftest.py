"""Shared in-memory fixtures — no file I/O, no database required."""

import pytest
from datetime import datetime, timedelta


def _ts(days_ago: float) -> str:
    return (datetime.now() - timedelta(days=days_ago)).isoformat(timespec="seconds")


@pytest.fixture
def sample_products():
    return {
        "P0001": {"product_id": "P0001", "name": "Khmer BBQ Set",   "category": "Food",    "price": 13.00, "banner_type": "standard",  "preferred_categories": []},
        "P0002": {"product_id": "P0002", "name": "Vitamin C Serum", "category": "Beauty",  "price": 45.00, "banner_type": "featured",   "preferred_categories": []},
        "P0003": {"product_id": "P0003", "name": "Yoga Class",      "category": "Service", "price": 20.00, "banner_type": "standard",   "preferred_categories": []},
        "P0004": {"product_id": "P0004", "name": "Linen Trousers",  "category": "Fashion", "price": 35.00, "banner_type": "flash_sale", "preferred_categories": []},
        "P0005": {"product_id": "P0005", "name": "Organic Granola", "category": "Food",    "price": 12.00, "banner_type": "standard",   "preferred_categories": []},
    }


@pytest.fixture
def sample_users():
    return {
        "U0001": {"user_id": "U0001", "name": "Sophea Lim", "preferred_categories": ["Food", "Beauty"], "age_group": "25-34"},
        "U0002": {"user_id": "U0002", "name": "Dara Chan",  "preferred_categories": ["Fashion"],         "age_group": "18-24"},
    }


@pytest.fixture
def sample_interactions():
    return [
        {"interaction_id": "I000001", "user_id": "U0001", "product_id": "P0001", "interaction_type": "view",  "timestamp": _ts(3)},
        {"interaction_id": "I000002", "user_id": "U0001", "product_id": "P0001", "interaction_type": "buy",   "timestamp": _ts(2)},
        {"interaction_id": "I000003", "user_id": "U0001", "product_id": "P0002", "interaction_type": "lead",  "timestamp": _ts(1)},
        {"interaction_id": "I000004", "user_id": "U0002", "product_id": "P0004", "interaction_type": "view",  "timestamp": _ts(2)},
        {"interaction_id": "I000005", "user_id": "U0002", "product_id": "P0004", "interaction_type": "buy",   "timestamp": _ts(1)},
        {"interaction_id": "I000006", "user_id": "U0001", "product_id": None,    "interaction_type": "visit", "timestamp": _ts(1)},
    ]
