export function money(n: number | null | undefined): string {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(n));
}

export function effectivePrice(p: { price: number; after_discount_price?: number | null }): number {
  return p.after_discount_price != null ? Number(p.after_discount_price) : Number(p.price);
}
