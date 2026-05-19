from fastapi import APIRouter, Query

from backend.config import DEFAULT_TOP_N
from backend.services.recommendation_service import get_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/home/{user_id}")
def home(user_id: int, top_n: int = Query(DEFAULT_TOP_N, ge=1, le=50)):
    recs = get_service().recommend_home(str(user_id), top_n=top_n)
    return {"user_id": user_id, "recommendations": recs}


@router.get("/trending")
def trending(top_n: int = Query(DEFAULT_TOP_N, ge=1, le=50)):
    return {"trending": get_service().trending(top_n=top_n)}


@router.post("/refresh")
def refresh():
    """Force a reload of users/products/interactions from MySQL."""
    get_service().refresh()
    return {"status": "ok"}
