"""Pydantic models shared by the API routes."""

from typing import Optional

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    user_id: int = Field(..., description="Employee id")
    product_id: int
    interaction_type: str = Field("view", pattern="^(view|lead|buy)$")


class SearchEventIn(BaseModel):
    user_id: Optional[int] = None
    query: str


class ProductOut(BaseModel):
    product_id: int
    name: str
    price: float
    discount_price: Optional[float] = None
    after_discount_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    description: Optional[str] = ""
    total_views: int = 0
    banner_type: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    page_type: Optional[str] = None


class RecommendedProductOut(ProductOut):
    final_score: Optional[float] = None
    content_score: Optional[float] = None
    collab_score: Optional[float] = None
    popularity_score: Optional[float] = None


class CategoryOut(BaseModel):
    category_id: int
    name: str
    page_type_id: Optional[int] = None
    page_type: Optional[str] = None
    product_count: int = 0


class UserOut(BaseModel):
    user_id: int
    name: str
    gender: Optional[str] = None
    education_level: Optional[str] = None
    employee_level_id: Optional[int] = None
