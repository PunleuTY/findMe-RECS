"""Write-side interaction logging into MySQL."""

from typing import Optional

from backend.database.connection import get_connection

_ACTION_BY_TYPE = {
    "view": "Just Exploring",
    "lead": "Call Me Later",
    "buy":  "Buy in telegram",
}


def _resolve_employee_context(user_id: int, cur) -> tuple[int, int]:
    cur.execute("SELECT client_id FROM employees WHERE id = %s LIMIT 1", (user_id,))
    emp = cur.fetchone()
    client_id = emp["client_id"] if emp else 1

    cur.execute(
        "SELECT crm_contact_id FROM benefit_me_engagements WHERE employee_id = %s ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    )
    eng = cur.fetchone()
    crm_contact_id = eng["crm_contact_id"] if eng else user_id
    return client_id, crm_contact_id


def log_interaction(user_id: int, product_id: int, interaction_type: str) -> None:
    itype = interaction_type.lower()
    if itype not in _ACTION_BY_TYPE:
        itype = "view"

    with get_connection() as conn:
        with conn.cursor() as cur:
            client_id, crm_contact_id = _resolve_employee_context(user_id, cur)
            if itype == "view":
                cur.execute(
                    "INSERT INTO crm_product_views (client_id, employee_id, crm_product_id, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
                    (client_id, user_id, product_id),
                )
            else:
                cur.execute(
                    "INSERT INTO benefit_me_engagements (client_id, employee_id, crm_contact_id, product_id, action_type, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                    (client_id, user_id, crm_contact_id, product_id, _ACTION_BY_TYPE[itype]),
                )
            conn.commit()


def log_search(user_id: Optional[int], query: str) -> None:
    if not query.strip():
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                client_id = None
                if user_id:
                    cur.execute("SELECT client_id FROM employees WHERE id = %s LIMIT 1", (user_id,))
                    emp = cur.fetchone()
                    client_id = emp["client_id"] if emp else None
                if client_id:
                    cur.execute(
                        "INSERT INTO benefit_me_search_histories (client_id, employee_id, search, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
                        (client_id, user_id, query[:255]),
                    )
                    conn.commit()
    except Exception:
        pass
