"""
One-time seeder: replaces crm_products and benefit_me_categories with
500 synthetic BenefitMe products following the taxonomy in db-revision-info.md.

Usage:
    python scripts/seed_synthetic_products.py

Requires the .env file at project root with DB_* credentials.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import pymysql
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_NAME     = os.getenv("DB_NAME", "findme_rs_db")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

random.seed(42)

# ---------------------------------------------------------------------------
# Taxonomy: category → (page_type_name, [sub_categories])
# ---------------------------------------------------------------------------
TAXONOMY = {
    "Fashion & Apparel": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "T-shirts", "Shirts (formal)", "Shirts (casual)", "Jeans", "Trousers",
            "Jackets", "Traditional wear", "Dresses", "Tops / Blouses", "Skirts",
            "Jeans / Pants", "Outerwear", "Boys clothing", "Girls clothing",
            "Infant wear", "Sneakers", "Formal shoes", "Sandals / Slippers",
            "Boots", "Bags (backpacks, handbags)", "Belts", "Hats / Caps", "Wallets",
        ],
        "gender_pool": ["men", "women", "kids", "unisex"],
        "price_range": (5, 120),
        "styles": ["casual", "formal", "streetwear", "sporty", "traditional"],
        "materials": ["cotton", "polyester", "denim", "linen", "silk", "wool", "leather", "nylon"],
        "colors": ["black", "white", "navy", "red", "blue", "grey", "green", "beige", "brown", "pink"],
        "brands": ["Zara", "H&M", "Uniqlo", "Levi's", "Nike", "Adidas", "Gap", "Forever 21", "Mango", "Pull&Bear"],
    },
    "Electronics & Devices": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Android phones", "iPhones", "Feature phones", "Laptops", "Desktops",
            "Monitors", "PC components", "Headphones", "Earbuds", "Speakers",
            "Smartwatches", "Smart home devices", "Fitness trackers",
            "Chargers", "Cables", "Power banks", "Cases",
        ],
        "gender_pool": ["unisex"],
        "price_range": (50, 1500),
        "styles": ["sporty", "casual"],
        "materials": ["plastic", "aluminum", "glass", "silicon", "metal"],
        "colors": ["black", "white", "silver", "gold", "space grey", "midnight"],
        "brands": ["Samsung", "Apple", "Sony", "Xiaomi", "Huawei", "Anker", "JBL", "Dell", "HP", "Lenovo"],
    },
    "Home & Living": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Beds", "Tables", "Chairs", "Sofas", "Storage",
            "Cookware", "Utensils", "Dinnerware", "Appliances",
            "Wall art", "Lighting", "Carpets", "Curtains",
            "Detergents", "Cleaning tools", "Disinfectants",
        ],
        "gender_pool": ["unisex"],
        "price_range": (5, 500),
        "styles": ["casual", "traditional", "formal"],
        "materials": ["wood", "metal", "plastic", "ceramic", "glass", "fabric", "bamboo"],
        "colors": ["white", "brown", "black", "beige", "grey", "natural wood"],
        "brands": ["IKEA", "Pyrex", "Tefal", "Philips", "OXO", "3M", "Scotch-Brite", "Rubbermaid", "Lodge", "Le Creuset"],
    },
    "Beauty & Personal Care": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Face wash", "Moisturizer", "Sunscreen", "Serums",
            "Lipstick", "Foundation", "Eye makeup", "Brushes",
            "Shampoo", "Conditioner", "Hair treatments",
            "Soap", "Deodorant", "Oral care",
        ],
        "gender_pool": ["women", "men", "unisex"],
        "price_range": (3, 80),
        "styles": ["casual"],
        "materials": ["natural", "organic", "mineral", "chemical-free", "paraben-free"],
        "colors": ["nude", "red", "pink", "coral", "berry", "clear"],
        "brands": ["L'Oreal", "Nivea", "Neutrogena", "Dove", "Garnier", "Cetaphil", "The Ordinary", "CeraVe", "Maybelline", "NYX"],
    },
    "Food & Groceries": {
        "page_type": "food",
        "product_type": "food",
        "sub_categories": [
            "Vegetables", "Fruits", "Meat & seafood",
            "Snacks", "Instant noodles", "Cereals",
            "Soft drinks", "Coffee / Tea", "Juices",
            "Rice / grains", "Cooking oil", "Condiments",
        ],
        "gender_pool": ["unisex"],
        "price_range": (1, 50),
        "styles": ["casual"],
        "materials": ["organic", "fresh", "packaged", "dried", "frozen"],
        "colors": [],
        "brands": ["Nestle", "Unilever", "Kellogg's", "Coca-Cola", "Pepsi", "Lays", "Maggi", "Lipton", "Nescafe", "Milo"],
    },
    "Books & Education": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Computer Science", "Mathematics", "Business",
            "Self-development", "Productivity", "Communication", "Leadership",
            "Story books", "Learning books",
            "Notebooks", "Pens", "Art supplies",
        ],
        "gender_pool": ["unisex"],
        "price_range": (2, 60),
        "styles": ["casual"],
        "materials": ["paper", "hardcover", "softcover", "recycled paper"],
        "colors": ["various"],
        "brands": ["Pearson", "McGraw-Hill", "Oxford", "Cambridge", "Penguin", "National Geographic", "Moleskine", "Pilot", "Staedtler", "Faber-Castell"],
    },
    "Sports & Outdoors": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Dumbbells", "Yoga mats", "Resistance bands",
            "Football", "Basketball", "Badminton",
            "Camping tents", "Backpacks", "Water bottles",
        ],
        "gender_pool": ["men", "women", "unisex"],
        "price_range": (5, 300),
        "styles": ["sporty", "casual"],
        "materials": ["rubber", "neoprene", "nylon", "polyester", "steel", "aluminum", "foam"],
        "colors": ["black", "blue", "red", "green", "orange", "grey"],
        "brands": ["Nike", "Adidas", "Decathlon", "Under Armour", "Reebok", "Coleman", "The North Face", "Hydro Flask", "Wilson", "Spalding"],
    },
    "Toys & Baby Products": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Educational toys", "Action figures", "Puzzle games",
            "Diapers", "Baby food", "Baby skincare",
            "Strollers", "Car seats", "Cribs",
        ],
        "gender_pool": ["kids", "unisex"],
        "price_range": (5, 300),
        "styles": ["casual"],
        "materials": ["plastic", "wood", "fabric", "foam", "cotton"],
        "colors": ["red", "blue", "yellow", "green", "pink", "multicolor"],
        "brands": ["LEGO", "Fisher-Price", "Huggies", "Pampers", "Graco", "Chicco", "Hasbro", "Mattel", "Vtech", "Infantino"],
    },
    "Automotive": {
        "page_type": "store",
        "product_type": "store",
        "sub_categories": [
            "Seat covers", "Air fresheners", "Phone mounts",
            "Engine oil", "Cleaning kits", "Tires",
        ],
        "gender_pool": ["men", "unisex"],
        "price_range": (5, 200),
        "styles": ["casual", "sporty"],
        "materials": ["leather", "neoprene", "rubber", "plastic", "microfiber"],
        "colors": ["black", "grey", "beige", "red", "blue"],
        "brands": ["3M", "Armor All", "Castrol", "Mobil", "Michelin", "Bosch", "Meguiar's", "Chemical Guys", "WD-40", "Rain-X"],
    },
}

SEASONS      = ["summer", "winter", "all-season", "spring", "autumn"]
AGE_GROUPS   = ["infant", "child", "teen", "adult"]
SIZE_RANGES  = ["XS", "S", "M", "L", "XL"]

# Sub-categories that map to specific product details
GENDER_SUB_MAP = {
    "Dresses": "women", "Tops / Blouses": "women", "Skirts": "women", "Girls clothing": "kids",
    "T-shirts": "men", "Shirts (formal)": "men", "Shirts (casual)": "men",
    "Jeans": "unisex", "Trousers": "unisex", "Jackets": "unisex",
    "Traditional wear": "unisex", "Boys clothing": "kids", "Infant wear": "kids",
    "Outerwear": "unisex", "Jeans / Pants": "unisex",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pick_gender(cat_info: dict, sub_cat: str) -> str:
    if sub_cat in GENDER_SUB_MAP:
        return GENDER_SUB_MAP[sub_cat]
    return random.choice(cat_info["gender_pool"])


def pick_age_group(gender: str, sub_cat: str) -> str:
    if "infant" in sub_cat.lower() or gender == "infant":
        return "infant"
    if gender == "kids" or "boys" in sub_cat.lower() or "girls" in sub_cat.lower():
        return random.choice(["child", "teen"])
    return random.choice(["teen", "adult"])


def gen_price(price_range: tuple) -> tuple:
    lo, hi = price_range
    price = round(random.uniform(lo, hi), 2)
    discount_pct = round(random.uniform(0.0, 0.40), 2)
    discount_amt = round(price * discount_pct, 2)
    final_price  = round(price - discount_amt, 2)
    return price, discount_pct * 100, discount_amt, final_price


def gen_rating() -> tuple:
    rating = round(random.uniform(1.0, 5.0), 1)
    review_count = random.randint(0, 10000)
    popularity = round(min(5.0, rating * 0.6 + (review_count / 10000) * 2.0), 1)
    return rating, review_count, popularity


def gen_created_at() -> str:
    days_ago = random.randint(0, 730)
    dt = datetime(2026, 5, 19) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def gen_product_code(category: str, idx: int) -> str:
    prefix = "".join(w[0] for w in category.split()[:3]).upper()
    return f"{prefix}-{idx:04d}"


def build_description(brand: str, category: str, sub_cat: str, gender: str,
                       age_group: str, material: list, season: str, style: str,
                       color: list, size_range: list, rating: float,
                       review_count: int, popularity: float, stock: int) -> str:
    return json.dumps({
        "brand": brand,
        "category": category,
        "sub_category": sub_cat,
        "gender_target": gender,
        "age_group": age_group,
        "material": material,
        "season": season,
        "style": style,
        "color": color,
        "size_range": size_range,
        "rating": rating,
        "review_count": review_count,
        "popularity_score": popularity,
        "stock": stock,
    }, ensure_ascii=False)


def build_tags(sub_cat: str, category: str, material: list, style: str,
               season: str, gender: str) -> str:
    tags = [
        sub_cat.lower().replace(" ", "-"),
        category.lower().replace(" ", "-").replace("&", "and"),
        material[0].lower() if material else "",
        style,
        season,
        gender,
    ]
    return json.dumps([t for t in tags if t], ensure_ascii=False)


# ---------------------------------------------------------------------------
# Distribution: how many products per category (total = 500)
# ---------------------------------------------------------------------------
DISTRIBUTION = {
    "Fashion & Apparel":      90,
    "Electronics & Devices":  55,
    "Home & Living":          55,
    "Beauty & Personal Care": 55,
    "Food & Groceries":       70,
    "Books & Education":      35,
    "Sports & Outdoors":      50,
    "Toys & Baby Products":   50,
    "Automotive":             40,
}
assert sum(DISTRIBUTION.values()) == 500, "Distribution must total 500"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def connect():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_page_type_ids(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM benefit_me_page_types")
        rows = cur.fetchall()
    return {r["name"]: r["id"] for r in rows}


def clear_and_rebuild_categories(conn, page_type_ids: dict) -> dict:
    """Truncate old categories (and unlink promotions), then insert new ones."""
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE crm_benefit_promotion_categories")
        cur.execute("TRUNCATE TABLE benefit_me_categories")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    cat_ids = {}
    with conn.cursor() as cur:
        for cat_name, info in TAXONOMY.items():
            pt_id = page_type_ids.get(info["page_type"])
            cur.execute(
                "INSERT INTO benefit_me_categories (page_type_id, name) VALUES (%s, %s)",
                (pt_id, cat_name),
            )
            cat_ids[cat_name] = cur.lastrowid
    conn.commit()
    print(f"  Inserted {len(cat_ids)} categories.")
    return cat_ids


def clear_products(conn):
    """Remove all product-dependent rows then truncate crm_products."""
    dependent = [
        "employee_products",
        "crm_benefit_sold_products",
        "crm_benefit_more_info_archives",
        "benefit_me_engagements",
        "benefit_me_reach_products",
        "crm_product_views",
        "crm_product_restaurants",
        "crm_product_stores",
        "crm_product_services",
        "crm_products",
    ]
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in dependent:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
            print(f"  Truncated {tbl}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()


def generate_products(cat_ids: dict) -> list[dict]:
    products = []
    idx = 1
    used_names: set = set()

    for cat_name, count in DISTRIBUTION.items():
        info = TAXONOMY[cat_name]
        cat_id = cat_ids[cat_name]
        sub_cats = info["sub_categories"]
        brands   = info["brands"]

        for _ in range(count):
            sub_cat = random.choice(sub_cats)
            brand   = random.choice(brands)
            gender  = pick_gender(info, sub_cat)
            age_grp = pick_age_group(gender, sub_cat)
            season  = random.choice(SEASONS)
            style   = random.choice(info["styles"])

            material = random.sample(info["materials"], k=min(2, len(info["materials"])))
            colors   = (random.sample(info["colors"], k=min(2, len(info["colors"])))
                        if info["colors"] else [])
            sizes    = (random.sample(SIZE_RANGES, k=random.randint(2, 5))
                        if cat_name == "Fashion & Apparel" else [])

            price, disc_pct, disc_amt, final_price = gen_price(info["price_range"])
            rating, review_count, popularity        = gen_rating()
            stock      = random.randint(0, 500)
            created_at = gen_created_at()
            total_views = int(review_count * random.uniform(1.5, 4.0))

            # Unique name
            base_name = f"{brand} {sub_cat}"
            candidate = base_name
            suffix = 1
            while candidate in used_names:
                candidate = f"{base_name} {suffix}"
                suffix += 1
            used_names.add(candidate)

            desc = build_description(
                brand, cat_name, sub_cat, gender, age_grp,
                material, season, style, colors, sizes,
                rating, review_count, popularity, stock,
            )
            tags = build_tags(sub_cat, cat_name, material, style, season, gender)

            products.append({
                "client_id":               1,
                "benefit_me_category_id":  cat_id,
                "name":                    candidate,
                "unit_price":              price,
                "is_active":               1,
                "product_type":            info["product_type"],
                "product_code":            gen_product_code(cat_name, idx),
                "discount_price":          disc_amt,
                "after_discount_price":    final_price,
                "discount_percentage":     round(disc_pct, 2),
                "description":             desc,
                "custom_description":      tags,
                "is_expired":              0,
                "review_status":           "approved",
                "total_views":             total_views,
                "created_at":              created_at,
            })
            idx += 1

    random.shuffle(products)
    return products


INSERT_SQL = """
INSERT INTO crm_products
  (client_id, benefit_me_category_id, name, unit_price, is_active,
   product_type, product_code, discount_price, after_discount_price,
   discount_percentage, description, custom_description, is_expired,
   review_status, total_views, created_at)
VALUES
  (%(client_id)s, %(benefit_me_category_id)s, %(name)s, %(unit_price)s,
   %(is_active)s, %(product_type)s, %(product_code)s, %(discount_price)s,
   %(after_discount_price)s, %(discount_percentage)s, %(description)s,
   %(custom_description)s, %(is_expired)s, %(review_status)s,
   %(total_views)s, %(created_at)s)
"""


def insert_products(conn, products: list[dict]):
    BATCH = 50
    inserted = 0
    with conn.cursor() as cur:
        for i in range(0, len(products), BATCH):
            batch = products[i : i + BATCH]
            cur.executemany(INSERT_SQL, batch)
            inserted += len(batch)
        conn.commit()
    return inserted


def main():
    print("Connecting to MySQL …")
    conn = connect()
    print(f"  Connected to {DB_NAME} on {DB_HOST}:{DB_PORT}")

    print("\nStep 1 — Resolving page_type IDs …")
    page_type_ids = get_page_type_ids(conn)
    print(f"  Found: {page_type_ids}")

    print("\nStep 2 — Clearing and rebuilding benefit_me_categories …")
    cat_ids = clear_and_rebuild_categories(conn, page_type_ids)

    print("\nStep 3 — Clearing existing crm_products (and dependents) …")
    clear_products(conn)

    print("\nStep 4 — Generating 500 synthetic products …")
    products = generate_products(cat_ids)
    print(f"  Generated {len(products)} products.")

    print("\nStep 5 — Inserting into crm_products …")
    n = insert_products(conn, products)
    print(f"  Inserted {n} products.")

    conn.close()
    print("\nDone. Database seeded successfully.")


if __name__ == "__main__":
    main()
