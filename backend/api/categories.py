from fastapi import APIRouter, HTTPException, Query

from backend.database import queries

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def list_categories():
    return {"categories": queries.list_categories()}


@router.get("/{category_id}")
def get_category(
    category_id: int,
    limit: int = Query(60, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    category = queries.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    products = queries.list_products(category_id=category_id, limit=limit, offset=offset)
    return {"category": category, "products": products}
