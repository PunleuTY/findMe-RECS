"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import ProductGrid from "@/components/ProductGrid";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import { getCurrentUserId } from "@/lib/session";
import type { Category, Product } from "@/lib/types";

export default function HomePage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [recs, setRecs] = useState<Product[]>([]);
  const [trending, setTrending] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(true);

  useEffect(() => {
    setUserId(getCurrentUserId());
    const onChange = () => setUserId(getCurrentUserId());
    window.addEventListener("findmers:user-changed", onChange);
    return () => window.removeEventListener("findmers:user-changed", onChange);
  }, []);

  useEffect(() => {
    api.trending(12).then(setTrending).catch(() => setTrending([]));
    api.listCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    setLoadingRecs(true);
    if (!userId) {
      setRecs([]);
      setLoadingRecs(false);
      return;
    }
    api
      .homeRecs(userId, 12)
      .then(setRecs)
      .catch(() => setRecs([]))
      .finally(() => setLoadingRecs(false));
  }, [userId]);

  return (
    <div className="space-y-12">
      <section className="rounded-2xl bg-gradient-to-r from-brand-500 to-brand-700 text-white px-6 py-10 sm:px-10 sm:py-14">
        <h1 className="text-3xl sm:text-4xl font-bold max-w-2xl">
          Discover products tailored for you
        </h1>
        <p className="mt-2 text-brand-50 max-w-2xl">
          Ranked by your interests, recent activity, and what others are engaging with right now.
        </p>
        {!userId && (
          <p className="mt-4 text-sm text-brand-100">
            Tip: select a user from the top-right corner to unlock personalised recommendations.
          </p>
        )}
      </section>

      <section>
        <SectionHeading
          title={userId ? "Recommended for you" : "Select a user for personalised picks"}
          subtitle={
            userId
              ? "Hybrid score = content affinity + collaborative filtering + popularity"
              : "Showing global trending until a user is selected"
          }
        />
        {loadingRecs ? (
          <div className="text-sm text-gray-500">Loading…</div>
        ) : userId ? (
          <ProductGrid products={recs} showScore emptyMessage="No recommendations yet — start browsing!" />
        ) : (
          <ProductGrid products={trending} />
        )}
      </section>

      <section>
        <SectionHeading
          title="Trending now"
          subtitle="Time-decayed popularity across all interactions"
          action={
            <Link href="/trending" className="text-sm text-brand-600 hover:underline">
              See all →
            </Link>
          }
        />
        <ProductGrid products={trending.slice(0, 8)} />
      </section>

      <section>
        <SectionHeading title="Browse by category" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {categories.slice(0, 12).map((c) => (
            <Link
              key={c.category_id}
              href={`/category/${c.category_id}`}
              className="card p-4 hover:bg-brand-50"
            >
              <div className="text-xs uppercase tracking-wide text-gray-400">
                {c.page_type || "category"}
              </div>
              <div className="font-semibold mt-1">{c.name}</div>
              <div className="text-xs text-gray-500 mt-1">{c.product_count} items</div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
