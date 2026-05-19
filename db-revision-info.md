# BenefitMe Product Dataset — Taxonomy & Spec

Defines the synthetic product catalogue used in the `findme_rs_db` database.
Applied via `scripts/seed_synthetic_products.py`.

---

## Category Taxonomy

### Fashion & Apparel — `store` (90 products)
| Sub-category |
|---|
| T-shirts, Shirts (formal), Shirts (casual), Jeans, Trousers, Jackets, Traditional wear |
| Dresses, Tops / Blouses, Skirts, Jeans / Pants, Outerwear |
| Boys clothing, Girls clothing, Infant wear |
| Sneakers, Formal shoes, Sandals / Slippers, Boots |
| Bags (backpacks, handbags), Belts, Hats / Caps, Wallets |

### Electronics & Devices — `store` (55 products)
| Sub-category |
|---|
| Android phones, iPhones, Feature phones |
| Laptops, Desktops, Monitors, PC components |
| Headphones, Earbuds, Speakers |
| Smartwatches, Smart home devices, Fitness trackers |
| Chargers, Cables, Power banks, Cases |

### Home & Living — `store` (55 products)
| Sub-category |
|---|
| Beds, Tables, Chairs, Sofas, Storage |
| Cookware, Utensils, Dinnerware, Appliances |
| Wall art, Lighting, Carpets, Curtains |
| Detergents, Cleaning tools, Disinfectants |

### Beauty & Personal Care — `store` (55 products)
| Sub-category |
|---|
| Face wash, Moisturizer, Sunscreen, Serums |
| Lipstick, Foundation, Eye makeup, Brushes |
| Shampoo, Conditioner, Hair treatments |
| Soap, Deodorant, Oral care |

### Food & Groceries — `food` (70 products)
| Sub-category |
|---|
| Vegetables, Fruits, Meat & seafood |
| Snacks, Instant noodles, Cereals |
| Soft drinks, Coffee / Tea, Juices |
| Rice / grains, Cooking oil, Condiments |

### Books & Education — `store` (35 products)
| Sub-category |
|---|
| Computer Science, Mathematics, Business |
| Self-development, Productivity, Communication, Leadership |
| Story books, Learning books |
| Notebooks, Pens, Art supplies |

### Sports & Outdoors — `store` (50 products)
| Sub-category |
|---|
| Dumbbells, Yoga mats, Resistance bands |
| Football, Basketball, Badminton |
| Camping tents, Backpacks, Water bottles |

### Toys & Baby Products — `store` (50 products)
| Sub-category |
|---|
| Educational toys, Action figures, Puzzle games |
| Diapers, Baby food, Baby skincare |
| Strollers, Car seats, Cribs |

### Automotive — `store` (40 products)
| Sub-category |
|---|
| Seat covers, Air fresheners, Phone mounts |
| Engine oil, Cleaning kits, Tires |

---

## Product Schema (how fields map to `crm_products`)

| Synthetic field | `crm_products` column | Notes |
|---|---|---|
| name | `name` | `"{Brand} {Sub-category}"`, deduplicated |
| price | `unit_price` | Per-category price ranges below |
| discount (0.0–0.40) | `discount_percentage` | Stored as `%` (e.g. 0.20 → 20.00) |
| price × discount | `discount_price` | Absolute discount amount |
| price − discount_price | `after_discount_price` | Final price paid |
| category, sub_category, brand, gender_target, age_group, material, season, style, color, size_range, rating, review_count, popularity_score, stock | `description` (JSON) | Full metadata blob |
| [sub_cat, category, material, style, season, gender] | `custom_description` (JSON array) | Keyword tags for search |
| — | `product_type` | `"food"` for Food & Groceries, `"store"` for all others |
| — | `review_status` | Always `"approved"` |
| — | `total_views` | Derived from review_count × random factor |

### `description` JSON structure

```json
{
  "brand": "Nike",
  "category": "Fashion & Apparel",
  "sub_category": "Sneakers",
  "gender_target": "unisex",
  "age_group": "adult",
  "material": ["rubber", "nylon"],
  "season": "all-season",
  "style": "sporty",
  "color": ["black", "white"],
  "size_range": ["S", "M", "L", "XL"],
  "rating": 4.2,
  "review_count": 3481,
  "popularity_score": 3.2,
  "stock": 187
}
```

---

## Pricing Rules

| Category | Price range (USD) |
|---|---|
| T-shirts | 5–25 |
| Shirts / Tops | 10–40 |
| Jeans / Trousers | 20–60 |
| Jackets / Outerwear | 30–120 |
| Footwear / Bags | 15–100 |
| Electronics | 50–1500 |
| Beauty | 3–80 |
| Food & Groceries | 1–50 |
| Sports & Outdoors | 5–300 |
| Toys & Baby | 5–300 |
| Automotive | 5–200 |
| Home & Living | 5–500 |
| Books & Education | 2–60 |

`discount` is drawn uniformly from `0.00–0.40`.
`after_discount_price = unit_price × (1 − discount)`.

---

## Popularity Logic

```
rating        ∈ [1.0, 5.0]
review_count  ∈ [0, 10 000]
popularity_score = min(5.0, rating × 0.6 + (review_count / 10 000) × 2.0)
total_views   = review_count × Uniform(1.5, 4.0)
```

---

## Re-seeding

```bash
python3 scripts/seed_synthetic_products.py
```

The script truncates all product-dependent tables before inserting, so it is safe to re-run.
Tables affected: `crm_products`, `benefit_me_categories`, `crm_product_views`,
`benefit_me_reach_products`, `benefit_me_engagements`, `employee_products`,
`crm_benefit_sold_products`, `crm_benefit_more_info_archives`,
`crm_product_restaurants`, `crm_product_stores`, `crm_product_services`,
`crm_benefit_promotion_categories`.

Tables **not** touched: `employees`, `benefit_me_page_types`, `crm_benefit_promotions`,
`benefit_me_payment_histories`.
