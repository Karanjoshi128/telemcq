"use client";

import { LayoutDashboard, LogOut, Menu, Search as SearchIcon, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { supabaseBrowser } from "@/lib/supabase/client";
import { ThemeToggle } from "./theme-toggle";

const LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/quiz", label: "Quiz", icon: null },
  { href: "/search", label: "Search", icon: SearchIcon },
];

export function Nav({ email }: { email?: string | null }) {
  const router = useRouter();
  const pathname = usePathname();
  const sb = supabaseBrowser();
  const [open, setOpen] = useState(false);

  async function signOut() {
    await sb.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-20 backdrop-blur border-b hairline bg-[rgb(var(--bg))]/70">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-2 px-4">
        <Link
          href="/dashboard"
          className="flex shrink-0 items-center gap-2 font-semibold"
          onClick={() => setOpen(false)}
        >
          <span
            className="inline-block h-3 w-3 rounded-full"
            style={{ background: "rgb(var(--accent))" }}
          />
          TeleMCQ
        </Link>

        <nav className="hidden items-center gap-1 text-sm sm:flex">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`btn-ghost ${pathname === l.href ? "border-[rgb(var(--accent))]" : ""}`}
            >
              {l.label}
            </Link>
          ))}
          <ThemeToggle />
          {email && (
            <button onClick={signOut} className="btn-ghost" title={email}>
              <LogOut className="h-4 w-4" />
            </button>
          )}
        </nav>

        <div className="flex items-center gap-1 sm:hidden">
          <ThemeToggle />
          <button
            aria-label="Menu"
            onClick={() => setOpen((v) => !v)}
            className="btn-ghost h-9 w-9 !p-0"
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t hairline sm:hidden">
          <nav className="mx-auto flex max-w-5xl flex-col gap-1 p-3">
            {LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className={`btn-ghost justify-start ${
                  pathname === l.href ? "border-[rgb(var(--accent))]" : ""
                }`}
              >
                {l.label}
              </Link>
            ))}
            {email && (
              <button onClick={signOut} className="btn-ghost justify-start">
                <LogOut className="h-4 w-4" /> Sign out
              </button>
            )}
            {email && (
              <div className="muted mt-1 truncate px-3 text-xs">{email}</div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
