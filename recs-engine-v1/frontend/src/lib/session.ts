"use client";

const KEY = "findmers.user_id";

export function getCurrentUserId(): number | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(KEY);
  return raw ? Number(raw) : null;
}

export function setCurrentUserId(id: number) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, String(id));
  window.dispatchEvent(new Event("findmers:user-changed"));
}

export function clearCurrentUserId() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(KEY);
  window.dispatchEvent(new Event("findmers:user-changed"));
}
