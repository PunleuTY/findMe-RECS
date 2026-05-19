"""Page-level SQL queries for the API routes."""

from typing import Optional

from backend.database.connection import fetch_all, fetch_one

_PRODUCT_SELECT = """
    cp.id                       AS product_id,
    cp.name                     AS name,
    cp.unit_price               AS price,
    cp.discount_price           AS discount_price,
    cp.after_discount_price     AS after_discount_price,
    cp.discount_percentage      AS discount_percentage,
    cp.description              AS description,
    cp.total_views              AS total_views,
    cp.product_type             AS banner_type,
    bmc.id                      AS category_id,
    bmc.name                    AS category,
    bpt.name                    AS page_type
"""

_PRODUCT_FROM = """
    FROM crm_products cp
    LEFT JOIN benefit_me_categories bmc ON bmc.id = cp.benefit_me_category_id
    LEFT JOIN benefit_me_page_types bpt ON bpt.id = bmc.page_type_id
"""

_PRODUCT_ACTIVE = """
    WHERE cp.is_active = 1
      AND cp.deleted_at IS NULL
"""


def list_products(
    category_id: Optional[int] = None,
    page_type: Optional[str] = None,
    limit: int = 60,
    offset: int = 0,
) -> list[dict]:
    where = [_PRODUCT_ACTIVE.strip()]
    params: list = []
    if category_id is not None:
        where.append("AND bmc.id = %s")
        params.append(category_id)
    if page_type is not None:
        where.append("AND bpt.name = %s")
        params.append(page_type)
    sql = f"""
        SELECT {_PRODUCT_SELECT}
        {_PRODUCT_FROM}
        {" ".join(where)}
        ORDER BY cp.total_views DESC, cp.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return fetch_all(sql, tuple(params))


def get_product(product_id: int) -> Optional[dict]:
    sql = f"SELECT {_PRODUCT_SELECT} {_PRODUCT_FROM} WHERE cp.id = %s LIMIT 1"
    return fetch_one(sql, (product_id,))


def list_categories() -> list[dict]:
    sql = """
        SELECT
            bmc.id               AS category_id,
            bmc.name             AS name,
            bpt.id               AS page_type_id,
            bpt.name             AS page_type,
            COUNT(cp.id)         AS product_count
        FROM benefit_me_categories bmc
        LEFT JOIN benefit_me_page_types bpt ON bpt.id = bmc.page_type_id
        LEFT JOIN crm_products cp
               ON cp.benefit_me_category_id = bmc.id
              AND cp.is_active = 1
              AND cp.deleted_at IS NULL
        WHERE bmc.deleted_at IS NULL
        GROUP BY bmc.id, bmc.name, bpt.id, bpt.name
        ORDER BY product_count DESC, bmc.name ASC
    """
    return fetch_all(sql)


def get_category(category_id: int) -> Optional[dict]:
    sql = """
        SELECT bmc.id AS category_id, bmc.name AS name, bpt.id AS page_type_id, bpt.name AS page_type
        FROM benefit_me_categories bmc
        LEFT JOIN benefit_me_page_types bpt ON bpt.id = bmc.page_type_id
        WHERE bmc.id = %s LIMIT 1
    """
    return fetch_one(sql, (category_id,))


def list_users(limit: int = 50) -> list[dict]:
    sql = """
        SELECT e.id AS user_id, e.name, e.gender, e.education_level, e.employee_level_id, e.birthday
        FROM employees e
        WHERE e.is_active = 1 AND e.deleted_at IS NULL
        ORDER BY e.id ASC LIMIT %s
    """
    return fetch_all(sql, (limit,))


def get_user(user_id: int) -> Optional[dict]:
    sql = """
        SELECT e.id AS user_id, e.name, e.gender, e.education_level, e.employee_level_id, e.birthday
        FROM employees e WHERE e.id = %s LIMIT 1
    """
    return fetch_one(sql, (user_id,))


def list_user_interactions(user_id: int, limit: int = 20) -> list[dict]:
    sql = f"""
        SELECT
            {_PRODUCT_SELECT},
            ev.interaction_type AS interaction_type,
            ev.ts               AS occurred_at
        FROM (
            SELECT crm_product_id AS product_id, employee_id, 'view' AS interaction_type,
                   created_at AS ts
            FROM crm_product_views WHERE employee_id = %s
            UNION ALL
            SELECT product_id, employee_id,
                   CASE action_type
                       WHEN 'Call Me Later'  THEN 'lead'
                       WHEN 'Just Exploring' THEN 'view'
                       WHEN 'Buy in telegram' THEN 'buy'
                       ELSE 'view'
                   END AS interaction_type,
                   created_at AS ts
            FROM benefit_me_engagements WHERE employee_id = %s
        ) ev
        JOIN crm_products cp ON cp.id = ev.product_id
        LEFT JOIN benefit_me_categories bmc ON bmc.id = cp.benefit_me_category_id
        LEFT JOIN benefit_me_page_types bpt ON bpt.id = bmc.page_type_id
        WHERE cp.is_active = 1 AND cp.deleted_at IS NULL
        ORDER BY ev.ts DESC LIMIT %s
    """
    return fetch_all(sql, (user_id, user_id, limit))
