"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { clearCurrentUserId, getCurrentUserId, setCurrentUserId } from "@/lib/session";
import type { User } from "@/lib/types";

export default function UserPicker() {
  const [users, setUsers] = useState<User[]>([]);
  const [current, setCurrent] = useState<number | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    api.listUsers().then(setUsers).catch(() => setUsers([]));
    setCurrent(getCurrentUserId());
    const onChange = () => setCurrent(getCurrentUserId());
    window.addEventListener("findmers:user-changed", onChange);
    return () => window.removeEventListener("findmers:user-changed", onChange);
  }, []);

  const currentUser = users.find((u) => u.user_id === current);

  return (
    <div className="relative">
      <button onClick={() => setOpen((v) => !v)} className="btn-secondary text-sm">
        {currentUser ? currentUser.name : "Select user…"}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-72 max-h-96 overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg z-40">
          {users.length === 0 && (
            <div className="px-4 py-3 text-sm text-gray-500">No users found</div>
          )}
          {users.map((u) => (
            <button
              key={u.user_id}
              onClick={() => { setCurrentUserId(u.user_id); setOpen(false); }}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                u.user_id === current ? "bg-brand-50 text-brand-700" : ""
              }`}
            >
              <div className="font-medium">{u.name}</div>
              <div className="text-xs text-gray-500">
                #{u.user_id} · {u.gender || "—"} · {u.education_level || "—"}
              </div>
            </button>
          ))}
          {current && (
            <button
              onClick={() => { clearCurrentUserId(); setOpen(false); }}
              className="w-full text-left px-4 py-2 text-sm text-red-600 border-t border-gray-100 hover:bg-red-50"
            >
              Clear selection
            </button>
          )}
        </div>
      )}
    </div>
  );
}
