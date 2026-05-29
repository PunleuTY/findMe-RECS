from typing import Optional

from fastapi import APIRouter, Query

from backend.config import DEFAULT_TOP_N
from backend.database.events import log_search
from backend.services.recommendation_service import get_service

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def search(
    q: str = Query(..., min_length=1),
    user_id: Optional[int] = None,
    top_n: int = Query(DEFAULT_TOP_N, ge=1, le=50),
):
    results = get_service().search(q, user_id=str(user_id) if user_id else "", top_n=top_n)
    log_search(user_id, q)
    return {"query": q, "user_id": user_id, "results": results}
