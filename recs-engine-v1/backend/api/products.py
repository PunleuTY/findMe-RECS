from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.database import queries
from backend.services.recommendation_service import get_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
def list_products(
    category_id: Optional[int] = None,
    page_type: Optional[str] = None,
    limit: int = Query(60, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return {"products": queries.list_products(category_id, page_type, limit, offset)}


@router.get("/{product_id}")
def get_product(product_id: int):
    product = queries.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    similar = get_service().similar_to(str(product_id), top_n=8)
    return {"product": product, "similar": similar}
