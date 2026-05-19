"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import type { Category } from "@/lib/types";

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);

  useEffect(() => {
    api.listCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  const byPageType = categories.reduce<Record<string, Category[]>>((acc, c) => {
    const k = c.page_type || "other";
    (acc[k] = acc[k] || []).push(c);
    return acc;
  }, {});

  return (
    <div className="space-y-10">
      <SectionHeading title="All categories" />
      {Object.entries(byPageType).map(([pageType, list]) => (
        <section key={pageType}>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
            {pageType}
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {list.map((c) => (
              <Link
                key={c.category_id}
                href={`/category/${c.category_id}`}
                className="card p-4 hover:bg-brand-50"
              >
                <div className="font-semibold">{c.name}</div>
                <div className="text-xs text-gray-500 mt-1">{c.product_count} items</div>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
