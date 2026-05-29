"""
Project-wide configuration: paths and algorithm constants.
All path resolution is relative to the project root.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR      = os.path.join(PROJECT_ROOT, "data")
GENERATED_DIR = os.path.join(DATA_DIR, "generated")

USERS_FILE        = os.path.join(GENERATED_DIR, "users.json")
PRODUCTS_FILE     = os.path.join(GENERATED_DIR, "products.json")
INTERACTIONS_FILE = os.path.join(GENERATED_DIR, "interactions.json")

# ── Interaction weights ───────────────────────────────────────────────────────
INTERACTION_WEIGHTS = {
    "view":   1,
    "search": 1,
    "visit":  0,
    "lead":   4,
    "rate":   4,
    "buy":    8,
    "claim":  8,
    "pay":    8,
}

# ── Algorithm constants ───────────────────────────────────────────────────────
TIME_DECAY_HALF_LIFE_DAYS = 7
CF_TOP_K_NEIGHBOURS = 10

COLD_CONTENT_BASE  = 0.30
COLD_COLLAB_BASE   = 0.10
CONTENT_GROWTH     = 0.008
COLLAB_GROWTH      = 0.003
MAX_CONTENT_WEIGHT = 0.50
MAX_COLLAB_WEIGHT  = 0.25

# ── Data generation defaults ──────────────────────────────────────────────────
GEN_N_USERS        = 150
GEN_N_PRODUCTS     = 300
GEN_N_PROMOTIONS   = 20
GEN_N_INTERACTIONS = 3_000
GEN_N_SEARCHES     = 500
GEN_N_FAVOURITES   = 400
GEN_N_BANNERS      = 10
GEN_RANDOM_SEED    = 42
