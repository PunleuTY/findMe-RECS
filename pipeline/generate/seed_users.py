"""
Generate 225 synthetic employees and their cold-start product assignments.

Split:
  180 training users   (80% of each persona group)
   45 validation users (20% of each persona group)
   25 real users in DB → test cohort, never modified

Persona distribution (225 total):
  tech_male_young          40  male    22-32
  fashion_female_young     40  female  20-30
  parent_any_mid           35  any     30-42
  professional_male_senior 35  male    35-50
  homemaker_female_mid     40  female  28-45
  budget_any_junior        35  any     18-26

Output:
  MySQL: employees (+225 rows), employee_products (~900 rows)
  File:  data/generated/user_personas.json  {user_id: persona_name}

Usage:
  python pipeline/generate/seed_users.py
  python pipeline/generate/seed_users.py --dry-run
"""

import argparse
import json
import os
import random
from datetime import date, timedelta
from pathlib import Path

import pymysql
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

random.seed(42)

# ── DB ────────────────────────────────────────────────────────────────────────
DB = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    database=os.getenv("DB_NAME", "findme_rs_db"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False,
)
CLIENT_ID = 1  # synthetic users belong to the demo client

# ── Cambodian name pools ──────────────────────────────────────────────────────
_MALE_FIRST = [
    "Dara", "Virak", "Kosal", "Channara", "Bunna", "Rithy", "Sokha", "Piseth",
    "Sovann", "Ratha", "Panha", "Makara", "Sophal", "Veasna", "Kimheng",
    "Borey", "Theara", "Samnang", "Vicheka", "Chanrith", "Raksmey", "Vuthy",
    "Menghour", "Seangly", "Kimsan",
]
_FEMALE_FIRST = [
    "Sophea", "Bopha", "Sreyleak", "Davy", "Chanthy", "Kolab", "Leakhena",
    "Sreymom", "Pisey", "Rachana", "Sothea", "Kunthea", "Chanda", "Sokneang",
    "Vimean", "Sreynich", "Malina", "Lyda", "Sokunthea", "Channary",
    "Dararith", "Somnang", "Kanha", "Kimly", "Rathana",
]
_SURNAMES = [
    "Chan", "Lim", "Ny", "Meas", "Phan", "Ty", "Sok", "Keo", "Heng", "Nget",
    "Ros", "Seng", "Long", "Oun", "Em", "Pen", "Khiev", "Tep", "Im", "Yem",
    "Chhun", "Vong", "Sar", "Penh", "Horn",
]

# ── Persona definitions ───────────────────────────────────────────────────────
PERSONAS = {
    "tech_male_young": {
        "gender": "male",
        "age_range": (22, 32),
        "education_pool": ["bachelor", "bachelor", "master", "vocational"],
        "level_pool": [1, 1, 2],
        "count": 40,
        "top_categories": ["Electronics & Devices", "Sports & Outdoors",
                           "Books & Education", "Fashion & Apparel"],
        "cat_weights": [5, 3, 2, 1],
    },
    "fashion_female_young": {
        "gender": "female",
        "age_range": (20, 30),
        "education_pool": ["high_school", "vocational", "bachelor", "bachelor"],
        "level_pool": [1, 1, 2],
        "count": 40,
        "top_categories": ["Fashion & Apparel", "Beauty & Personal Care",
                           "Food & Groceries", "Books & Education"],
        "cat_weights": [5, 4, 2, 1],
    },
    "parent_any_mid": {
        "gender": None,
        "age_range": (30, 42),
        "education_pool": ["bachelor", "bachelor", "master", "vocational"],
        "level_pool": [1, 2, 2, 3],
        "count": 35,
        "top_categories": ["Toys & Baby Products", "Food & Groceries",
                           "Home & Living", "Automotive"],
        "cat_weights": [5, 4, 3, 2],
    },
    "professional_male_senior": {
        "gender": "male",
        "age_range": (35, 50),
        "education_pool": ["bachelor", "master", "master"],
        "level_pool": [2, 2, 3, 3],
        "count": 35,
        "top_categories": ["Automotive", "Electronics & Devices",
                           "Books & Education", "Sports & Outdoors"],
        "cat_weights": [4, 4, 3, 2],
    },
    "homemaker_female_mid": {
        "gender": "female",
        "age_range": (28, 45),
        "education_pool": ["high_school", "vocational", "bachelor", "bachelor"],
        "level_pool": [1, 1, 2],
        "count": 40,
        "top_categories": ["Home & Living", "Food & Groceries",
                           "Beauty & Personal Care", "Toys & Baby Products"],
        "cat_weights": [5, 5, 3, 2],
    },
    "budget_any_junior": {
        "gender": None,
        "age_range": (18, 26),
        "education_pool": ["high_school", "high_school", "vocational", "bachelor"],
        "level_pool": [1, 1, 1, 2],
        "count": 35,
        "top_categories": ["Food & Groceries", "Fashion & Apparel",
                           "Books & Education", "Sports & Outdoors"],
        "cat_weights": [4, 3, 3, 2],
    },
}

assert sum(p["count"] for p in PERSONAS.values()) == 225


# ── Helpers ───────────────────────────────────────────────────────────────────

def _birthday(age_range: tuple) -> date:
    lo, hi = age_range
    age_days = random.randint(lo * 365, hi * 365)
    return date.today() - timedelta(days=age_days)


def _email(name: str, uid_suffix: int) -> str:
    return f"{name.lower().replace(' ', '.')}_{uid_suffix}@benefitme.test"


def _gender(persona: dict) -> str:
    if persona["gender"]:
        return persona["gender"]
    return random.choice(["male", "female"])


def connect() -> pymysql.Connection:
    return pymysql.connect(**DB)


# ── Step 1: protect real users ────────────────────────────────────────────────

def get_real_user_ids(conn) -> set:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM employees")
        return {r["id"] for r in cur.fetchall()}


# ── Step 2: wipe previous synthetic users ─────────────────────────────────────

def clear_synthetic_users(conn, real_ids: set, dry_run: bool):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM employees")
        all_ids = [r["id"] for r in cur.fetchall()]
    synth_ids = [i for i in all_ids if i not in real_ids]
    if not synth_ids:
        print("  No synthetic users found, skipping clear.")
        return
    print(f"  Removing {len(synth_ids)} existing synthetic users...")
    if not dry_run:
        with conn.cursor() as cur:
            fmt = ",".join(["%s"] * len(synth_ids))
            cur.execute(f"DELETE FROM employee_products WHERE employee_id IN ({fmt})", synth_ids)
            cur.execute(f"DELETE FROM employees WHERE id IN ({fmt})", synth_ids)
        conn.commit()


# ── Step 3: load category → product mapping ───────────────────────────────────

def load_category_products(conn) -> dict:
    """Returns {category_name: [product_id, ...]}"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT cp.id AS product_id, bmc.name AS category
            FROM crm_products cp
            JOIN benefit_me_categories bmc ON bmc.id = cp.benefit_me_category_id
            WHERE cp.is_active = 1 AND cp.deleted_at IS NULL
            """
        )
        rows = cur.fetchall()
    mapping: dict = {}
    for r in rows:
        mapping.setdefault(r["category"], []).append(r["product_id"])
    return mapping


# ── Step 4: generate employee rows ───────────────────────────────────────────

def generate_employees(personas: dict) -> list[dict]:
    rows = []
    counter = 1
    for persona_name, cfg in personas.items():
        for _ in range(cfg["count"]):
            gender = _gender(cfg)
            first  = random.choice(_MALE_FIRST if gender == "male" else _FEMALE_FIRST)
            last   = random.choice(_SURNAMES)
            name   = f"{first} {last}"
            bday   = _birthday(cfg["age_range"])
            edu    = random.choice(cfg["education_pool"])
            level  = random.choice(cfg["level_pool"])
            rows.append({
                "client_id":         CLIENT_ID,
                "name":              name,
                "email":             _email(name, counter),
                "gender":            gender,
                "birthday":          bday.isoformat(),
                "education_level":   edu,
                "employee_level_id": level,
                "is_active":         1,
                "_persona":          persona_name,  # kept in memory, not written to DB
            })
            counter += 1
    random.shuffle(rows)
    return rows


# ── Step 5: insert employees, collect new IDs ─────────────────────────────────

_EMP_SQL = """
INSERT INTO employees
  (client_id, name, email, gender, birthday, education_level, employee_level_id, is_active)
VALUES
  (%(client_id)s, %(name)s, %(email)s, %(gender)s, %(birthday)s,
   %(education_level)s, %(employee_level_id)s, %(is_active)s)
"""


def insert_employees(conn, rows: list[dict], dry_run: bool) -> list[dict]:
    """Returns rows with '_id' populated from lastrowid."""
    if dry_run:
        for i, r in enumerate(rows, start=99000):
            r["_id"] = i
        return rows

    with conn.cursor() as cur:
        for r in rows:
            cur.execute(_EMP_SQL, r)
            r["_id"] = cur.lastrowid
    conn.commit()
    return rows


# ── Step 6: build employee_products ──────────────────────────────────────────

def build_employee_products(rows: list[dict], cat_products: dict,
                             personas: dict) -> list[tuple]:
    """Returns [(employee_id, product_id), ...] — 3-5 products per user."""
    assignments = []
    for row in rows:
        cfg = personas[row["_persona"]]
        n_assign = random.randint(3, 5)

        # Sample category weighted by persona weights, then pick a product from it
        categories = random.choices(
            cfg["top_categories"],
            weights=cfg["cat_weights"],
            k=n_assign * 3,  # oversample, deduplicate below
        )
        seen_products: set = set()
        for cat in categories:
            if len(seen_products) >= n_assign:
                break
            products = cat_products.get(cat, [])
            if not products:
                continue
            pid = random.choice(products)
            seen_products.add(pid)

        for pid in seen_products:
            assignments.append((row["_id"], pid))
    return assignments


def insert_employee_products(conn, assignments: list[tuple], dry_run: bool):
    if dry_run:
        return
    sql = "INSERT IGNORE INTO employee_products (employee_id, crm_product_id) VALUES (%s, %s)"
    BATCH = 100
    with conn.cursor() as cur:
        for i in range(0, len(assignments), BATCH):
            cur.executemany(sql, assignments[i: i + BATCH])
    conn.commit()


# ── Step 7: save persona metadata file ───────────────────────────────────────

def save_persona_map(rows: list[dict], dry_run: bool):
    out_dir = PROJECT_ROOT / "data" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    persona_map = {str(r["_id"]): r["_persona"] for r in rows}
    path = out_dir / "user_personas.json"
    if not dry_run:
        path.write_text(json.dumps(persona_map, indent=2))
    print(f"  Persona map → {path}  ({len(persona_map)} entries)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main(dry_run: bool = False):
    tag = " [DRY RUN]" if dry_run else ""
    print(f"\n=== seed_users.py{tag} ===")

    conn = connect()
    print(f"  Connected to {DB['database']}@{DB['host']}")

    print("\nStep 1 — Identifying real users...")
    real_ids = get_real_user_ids(conn)
    print(f"  Real users to protect: {len(real_ids)}")

    print("\nStep 2 — Clearing previous synthetic users...")
    clear_synthetic_users(conn, real_ids, dry_run)

    print("\nStep 3 — Loading category → product map...")
    cat_products = load_category_products(conn)
    print(f"  Categories: {len(cat_products)}, total products: {sum(len(v) for v in cat_products.values())}")

    print("\nStep 4 — Generating 225 synthetic employees...")
    rows = generate_employees(PERSONAS)
    persona_counts = {}
    for r in rows:
        persona_counts[r["_persona"]] = persona_counts.get(r["_persona"], 0) + 1
    for p, n in persona_counts.items():
        print(f"  {p:<30s} {n} users")

    print("\nStep 5 — Inserting employees...")
    rows = insert_employees(conn, rows, dry_run)
    print(f"  Inserted {len(rows)} employees.")

    print("\nStep 6 — Building employee_products (cold-start)...")
    assignments = build_employee_products(rows, cat_products, PERSONAS)
    insert_employee_products(conn, assignments, dry_run)
    avg = len(assignments) / len(rows)
    print(f"  Inserted {len(assignments)} assignments (~{avg:.1f} per user).")

    print("\nStep 7 — Saving persona map...")
    save_persona_map(rows, dry_run)

    conn.close()

    print(f"\n{'DRY RUN — nothing written.' if dry_run else 'Done.'}")
    print(f"  Total employees in DB after run: {len(real_ids) + (0 if dry_run else len(rows))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing to DB")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
