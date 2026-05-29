"use client";

import { useEffect, useState } from "react";
import ProductGrid from "@/components/ProductGrid";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import type { Category, Product } from "@/lib/types";

export default function CategoryPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [category, setCategory] = useState<Category | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getCategory(id, 100)
      .then(({ category, products }) => {
        setCategory(category);
        setProducts(products);
      })
      .catch(() => {
        setCategory(null);
        setProducts([]);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-sm text-gray-500">Loading…</div>;
  if (!category) return <div className="text-sm text-gray-500">Category not found.</div>;

  return (
    <div>
      <SectionHeading
        title={category.name}
        subtitle={`${products.length} items · ${category.page_type || "category"}`}
      />
      <ProductGrid products={products} />
    </div>
  );
}
