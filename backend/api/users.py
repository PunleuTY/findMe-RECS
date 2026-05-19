from fastapi import APIRouter, HTTPException, Query

from backend.database import queries

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def list_users(limit: int = Query(50, ge=1, le=200)):
    return {"users": queries.list_users(limit)}


@router.get("/{user_id}")
def get_user(user_id: int):
    user = queries.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    history = queries.list_user_interactions(user_id, limit=20)
    return {"user": user, "history": history}
