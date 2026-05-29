"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import ProductGrid from "@/components/ProductGrid";
import SectionHeading from "@/components/SectionHeading";
import { api } from "@/lib/api";
import { effectivePrice, money } from "@/lib/format";
import { getCurrentUserId } from "@/lib/session";
import { trackEvent } from "@/lib/tracker";
import type { Product } from "@/lib/types";

export default function ProductDetailPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [product, setProduct] = useState<Product | null>(null);
  const [similar, setSimilar] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionDone, setActionDone] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setActionDone(null);
    api
      .getProduct(id)
      .then(({ product, similar }) => {
        setProduct(product);
        setSimilar(similar);
        trackEvent(id, "view");
      })
      .catch(() => {
        setProduct(null);
        setSimilar([]);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-sm text-gray-500">Loading…</div>;
  if (!product) return <div className="text-sm text-gray-500">Product not found.</div>;

  const price = effectivePrice(product);
  const original = Number(product.price);
  const hasDiscount = price < original;

  function act(kind: "lead" | "buy") {
    const uid = getCurrentUserId();
    if (!uid) {
      setActionDone("Please select a user first (top-right).");
      return;
    }
    trackEvent(id, kind);
    setActionDone(
      kind === "lead" ? "Interest logged — we'll follow up." : "Order intent logged.",
    );
  }

  return (
    <div className="space-y-10">
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="aspect-square rounded-2xl bg-gradient-to-br from-brand-50 to-gray-100 flex items-center justify-center text-brand-600 font-bold text-7xl">
          {product.name?.slice(0, 1).toUpperCase() || "?"}
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {product.page_type && <span className="capitalize">{product.page_type}</span>}
            {product.page_type && product.category && <span>·</span>}
            {product.category && (
              <Link href={`/category/${product.category_id}`} className="text-brand-600 hover:underline">
                {product.category}
              </Link>
            )}
          </div>
          <h1 className="text-3xl font-bold mt-2">{product.name}</h1>
          <div className="mt-4 flex items-baseline gap-3">
            <span className="text-3xl font-bold text-brand-700">{money(price)}</span>
            {hasDiscount && (
              <>
                <span className="text-lg text-gray-400 line-through">{money(original)}</span>
                <span className="chip bg-red-50 text-red-600">
                  -{Math.round(((original - price) / original) * 100)}%
                </span>
              </>
            )}
          </div>
          {product.description && (
            <p className="text-gray-700 mt-6 whitespace-pre-wrap leading-relaxed">
              {product.description}
            </p>
          )}
          <dl className="mt-6 grid grid-cols-2 gap-3 text-sm">
            {product.banner_type && (
              <><dt className="text-gray-500">Type</dt><dd>{product.banner_type}</dd></>
            )}
            {product.total_views != null && (
              <><dt className="text-gray-500">Total views</dt><dd>{product.total_views}</dd></>
            )}
            {product.discount_percentage != null && (
              <><dt className="text-gray-500">Discount</dt><dd>{Number(product.discount_percentage)}%</dd></>
            )}
          </dl>
          <div className="mt-8 flex gap-3">
            <button className="btn-primary" onClick={() => act("buy")}>Buy now</button>
            <button className="btn-secondary" onClick={() => act("lead")}>Interested</button>
          </div>
          {actionDone && <div className="mt-3 text-sm text-brand-700">{actionDone}</div>}
        </div>
      </div>

      <section>
        <SectionHeading title="Similar in this category" />
        <ProductGrid products={similar} emptyMessage="No related items found." />
      </section>
    </div>
  );
}
