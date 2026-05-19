"""
MySQL data loader for the recommender service.

Returns the (users, products, interactions) tuple that all algorithm modules expect.
Replace load_data() with a different source (CSV, API) without touching algorithm code.
"""

from datetime import date

from ml.config import INTERACTION_WEIGHTS
from backend.database.connection import fetch_all


def _age_group(birthday) -> str:
    if birthday is None:
        return "unknown"
    if isinstance(birthday, str):
        try:
            birthday = date.fromisoformat(birthday)
        except ValueError:
            return "unknown"
    age = (date.today() - birthday).days // 365
    if age < 20:
        return "under-20"
    decade = (age // 10) * 10
    return f"{decade}-{decade + 9}"


def load_data() -> tuple[dict, dict, list]:
    users = _load_users()
    products = _load_products()
    interactions = _load_interactions()
    return users, products, interactions


def _load_users() -> dict:
    rows = fetch_all(
        """
        SELECT
            e.id, e.name, e.birthday, e.gender, e.education_level,
            e.employee_level_id,
            GROUP_CONCAT(DISTINCT bmc.name ORDER BY bmc.name SEPARATOR ',') AS preferred_categories
        FROM employees e
        LEFT JOIN employee_products     ep  ON ep.employee_id      = e.id
        LEFT JOIN crm_products          cp  ON cp.id               = ep.crm_product_id
        LEFT JOIN benefit_me_categories bmc ON bmc.id              = cp.benefit_me_category_id
        WHERE e.is_active = 1 AND e.deleted_at IS NULL
        GROUP BY e.id, e.name, e.birthday, e.gender, e.education_level, e.employee_level_id
        """
    )
    users: dict = {}
    for row in rows:
        uid = str(row["id"])
        raw = row.get("preferred_categories") or ""
        cats = [c.strip() for c in raw.split(",") if c.strip()] if raw else []
        users[uid] = {
            "user_id":              uid,
            "name":                 row["name"],
            "age_group":            _age_group(row.get("birthday")),
            "gender":               row.get("gender") or "unknown",
            "education_level":      row.get("education_level") or "unknown",
            "employee_level_id":    row.get("employee_level_id"),
            "preferred_categories": cats,
        }
    return users


def _load_products() -> dict:
    rows = fetch_all(
        """
        SELECT
            cp.id, cp.name, cp.unit_price, cp.product_type,
            cp.discount_price, cp.after_discount_price,
            cp.discount_percentage, cp.description, cp.total_views,
            bmc.name AS category,
            bpt.name AS page_type
        FROM crm_products cp
        LEFT JOIN benefit_me_categories bmc ON bmc.id = cp.benefit_me_category_id
        LEFT JOIN benefit_me_page_types bpt ON bpt.id = bmc.page_type_id
        WHERE cp.is_active = 1 AND cp.deleted_at IS NULL
        """
    )
    products: dict = {}
    for row in rows:
        pid = str(row["id"])
        products[pid] = {
            "product_id":           pid,
            "name":                 row["name"],
            "category":             row.get("category") or "uncategorized",
            "page_type":            row.get("page_type") or "unknown",
            "price":                float(row.get("unit_price") or 0),
            "banner_type":          row.get("product_type") or "crm_product",
            "discount_price":       row.get("discount_price"),
            "after_discount_price": row.get("after_discount_price"),
            "discount_percentage":  row.get("discount_percentage"),
            "description":          row.get("description") or "",
            "total_views":          int(row.get("total_views") or 0),
        }
    return products


def _load_interactions() -> list:
    rows = fetch_all(
        """
        SELECT user_id, product_id, interaction_type, ts AS timestamp
        FROM (
            SELECT pv.employee_id AS user_id, pv.crm_product_id AS product_id,
                   'view' AS interaction_type, pv.created_at AS ts
            FROM crm_product_views pv
            UNION ALL
            SELECT rp.employee_id, rp.crm_product_id, 'view',
                   COALESCE(rp.viewed_at, rp.created_at)
            FROM benefit_me_reach_products rp
            UNION ALL
            SELECT eng.employee_id, eng.product_id,
                   CASE eng.action_type
                       WHEN 'Call Me Later'   THEN 'lead'
                       WHEN 'Just Exploring'  THEN 'view'
                       WHEN 'Buy in telegram' THEN 'buy'
                       ELSE 'view'
                   END,
                   eng.created_at
            FROM benefit_me_engagements eng
            UNION ALL
            SELECT mia.employee_customer_id, mia.product_id,
                   CASE mia.action_type
                       WHEN 'Call Me Later'   THEN 'lead'
                       WHEN 'Just Exploring'  THEN 'view'
                       WHEN 'Buy in telegram' THEN 'buy'
                       ELSE 'view'
                   END,
                   mia.created_at
            FROM crm_benefit_more_info_archives mia
        ) all_events
        ORDER BY timestamp DESC
        """
    )
    out: list = []
    for r in rows:
        ts = r["timestamp"]
        if hasattr(ts, "isoformat"):
            ts = ts.isoformat()
        itype = r["interaction_type"]
        out.append({
            "user_id":          str(r["user_id"]),
            "product_id":       str(r["product_id"]),
            "interaction_type": itype,
            "weight":           INTERACTION_WEIGHTS.get(itype, 1),
            "timestamp":        ts,
        })
    return out
