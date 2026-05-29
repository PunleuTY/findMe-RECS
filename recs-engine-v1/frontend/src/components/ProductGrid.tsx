import type { Product } from "@/lib/types";
import ProductCard from "./ProductCard";

export default function ProductGrid({
  products,
  showScore = false,
  emptyMessage = "No products found.",
}: {
  products: Product[];
  showScore?: boolean;
  emptyMessage?: string;
}) {
  if (!products.length) {
    return <div className="text-center py-16 text-gray-500 text-sm">{emptyMessage}</div>;
  }
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      {products.map((p) => (
        <ProductCard key={String(p.product_id)} product={p} showScore={showScore} />
      ))}
    </div>
  );
}
