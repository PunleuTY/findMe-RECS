import type { Category, HistoryItem, Product, User } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init });
  if (!res.ok) throw new Error(`API ${res.status} ${path}`);
  return res.json();
}

export const api = {
  homeRecs: (userId: number, topN = 12) =>
    get<{ recommendations: Product[] }>(`/api/recommendations/home/${userId}?top_n=${topN}`).then(
      (r) => r.recommendations,
    ),

  trending: (topN = 12) =>
    get<{ trending: Product[] }>(`/api/recommendations/trending?top_n=${topN}`).then(
      (r) => r.trending,
    ),

  listProducts: (params: { category_id?: number; page_type?: string; limit?: number; offset?: number } = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return get<{ products: Product[] }>(`/api/products${qs.toString() ? `?${qs}` : ""}`).then(
      (r) => r.products,
    );
  },

  getProduct: (id: number) =>
    get<{ product: Product; similar: Product[] }>(`/api/products/${id}`),

  listCategories: () =>
    get<{ categories: Category[] }>("/api/categories").then((r) => r.categories),

  getCategory: (id: number, limit = 60, offset = 0) =>
    get<{ category: Category; products: Product[] }>(
      `/api/categories/${id}?limit=${limit}&offset=${offset}`,
    ),

  search: (q: string, userId?: number) => {
    const qs = new URLSearchParams({ q });
    if (userId) qs.set("user_id", String(userId));
    return get<{ query: string; results: Product[] }>(`/api/search?${qs}`).then((r) => r.results);
  },

  listUsers: () => get<{ users: User[] }>("/api/users").then((r) => r.users),

  getUser: (id: number) =>
    get<{ user: User; history: HistoryItem[] }>(`/api/users/${id}`),

  logEvent: (event: { user_id: number; product_id: number; interaction_type: "view" | "lead" | "buy" }) =>
    fetch(`${BASE}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(event),
      keepalive: true,
    }),
};
