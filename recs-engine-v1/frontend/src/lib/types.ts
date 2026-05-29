export interface Product {
  product_id: number | string;
  name: string;
  price: number;
  discount_price?: number | null;
  after_discount_price?: number | null;
  discount_percentage?: number | null;
  description?: string;
  total_views?: number;
  banner_type?: string;
  category_id?: number | null;
  category?: string;
  page_type?: string;
  final_score?: number;
  content_score?: number;
  collab_score?: number;
  popularity_score?: number;
}

export interface Category {
  category_id: number;
  name: string;
  page_type_id?: number | null;
  page_type?: string;
  product_count: number;
}

export interface User {
  user_id: number;
  name: string;
  gender?: string;
  education_level?: string;
  employee_level_id?: number | null;
  birthday?: string | null;
}

export interface HistoryItem extends Product {
  interaction_type: "view" | "lead" | "buy";
  occurred_at: string;
}
