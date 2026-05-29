"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import UserPicker from "./UserPicker";

export default function Header() {
  const router = useRouter();
  const [q, setQ] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    router.push(`/search?q=${encodeURIComponent(q.trim())}`);
  }

  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-6">
        <Link href="/" className="text-xl font-bold text-brand-600">
          FindMe RS
        </Link>
        <nav className="hidden sm:flex items-center gap-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-brand-600">Home</Link>
          <Link href="/trending" className="hover:text-brand-600">Trending</Link>
          <Link href="/categories" className="hover:text-brand-600">Categories</Link>
        </nav>
        <form onSubmit={submit} className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search products, categories…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </form>
        <UserPicker />
      </div>
    </header>
  );
}
