"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import ProductGrid from "@/components/ProductGrid";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import { getCurrentUserId } from "@/lib/session";
import type { Product } from "@/lib/types";

export default function SearchPage() {
  const params = useSearchParams();
  const q = params.get("q") || "";
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!q) return;
    setLoading(true);
    const userId = getCurrentUserId();
    api
      .search(q, userId ?? undefined)
      .then(setResults)
      .catch(() => setResults([]))
      .finally(() => setLoading(false));
  }, [q]);

  return (
    <div>
      <SectionHeading
        title={q ? `Results for "${q}"` : "Search"}
        subtitle={
          q
            ? `${results.length} matches, re-ranked by your taste profile`
            : "Type a query in the search bar above"
        }
      />
      {loading ? (
        <div className="text-sm text-gray-500">Searching…</div>
      ) : (
        <ProductGrid
          products={results}
          showScore
          emptyMessage={q ? "No products matched your search." : "Try searching for something."}
        />
      )}
    </div>
  );
}
