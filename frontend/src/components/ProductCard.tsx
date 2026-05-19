"use client";

import Link from "next/link";
import { effectivePrice, money } from "@/lib/format";
import type { Product } from "@/lib/types";

export default function ProductCard({
  product,
  showScore = false,
}: {
  product: Product;
  showScore?: boolean;
}) {
  const price = effectivePrice(product);
  const originalPrice = Number(product.price);
  const hasDiscount = price < originalPrice;

  return (
    <Link href={`/products/${product.product_id}`} className="card block p-4 group">
      <div className="aspect-[4/3] mb-3 rounded-lg bg-gradient-to-br from-brand-50 to-gray-100 flex items-center justify-center text-brand-600 font-semibold text-2xl">
        {product.name?.slice(0, 1).toUpperCase() || "?"}
      </div>
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-gray-900 line-clamp-2 group-hover:text-brand-600">
          {product.name}
        </h3>
        {hasDiscount && (
          <span className="chip bg-red-50 text-red-600">
            -{Math.round(((originalPrice - price) / originalPrice) * 100)}%
          </span>
        )}
      </div>
      {product.category && (
        <div className="text-xs text-gray-500 mt-1">{product.category}</div>
      )}
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-base font-bold text-brand-700">{money(price)}</span>
        {hasDiscount && (
          <span className="text-xs text-gray-400 line-through">{money(originalPrice)}</span>
        )}
      </div>
      {showScore && product.final_score != null && (
        <div className="mt-2 text-[11px] text-gray-400 flex gap-2">
          <span>score {product.final_score?.toFixed(3)}</span>
          <span>·</span>
          <span>pop {product.popularity_score?.toFixed(2)}</span>
        </div>
      )}
    </Link>
  );
}
