from fastapi import APIRouter, HTTPException

from backend.api.schemas import EventIn
from backend.database.events import log_interaction

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("")
def post_event(event: EventIn):
    try:
        log_interaction(event.user_id, event.product_id, event.interaction_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log event: {e}")
    return {"status": "ok"}
