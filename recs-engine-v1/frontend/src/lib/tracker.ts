"use client";

import { api } from "./api";
import { getCurrentUserId } from "./session";

export function trackEvent(
  productId: number,
  interactionType: "view" | "lead" | "buy",
) {
  const userId = getCurrentUserId();
  if (!userId) return;
  api
    .logEvent({ user_id: userId, product_id: productId, interaction_type: interactionType })
    .catch(() => {});
}
