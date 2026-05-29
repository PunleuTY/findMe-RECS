"use client";

import { useEffect, useState } from "react";
import ProductGrid from "@/components/ProductGrid";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import type { Product } from "@/lib/types";

export default function TrendingPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .trending(48)
      .then(setProducts)
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <SectionHeading
        title="Trending"
        subtitle="Popularity ranked with a 7-day half-life time decay"
      />
      {loading ? (
        <div className="text-sm text-gray-500">Loading…</div>
      ) : (
        <ProductGrid products={products} />
      )}
    </div>
  );
}
