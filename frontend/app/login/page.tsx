"use client";

import { useState } from "react";
import { toast } from "sonner";
import { supabaseBrowser } from "@/lib/supabase/client";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LoginPage() {
  const sb = supabaseBrowser();
  const [loading, setLoading] = useState(false);

  async function signInGoogle() {
    setLoading(true);
    const { error } = await sb.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) {
      toast.error(error.message);
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <header className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <div className="font-semibold">TeleMCQ</div>
        <ThemeToggle />
      </header>
      <div className="mx-auto mt-24 max-w-sm px-4">
        <div className="panel p-8 text-center">
          <h1 className="text-2xl font-bold">Sign in</h1>
          <p className="muted mt-2 text-sm">
            Use your Google account to continue.
          </p>
          <button
            onClick={signInGoogle}
            disabled={loading}
            className="btn-primary mt-6 w-full"
          >
            {loading ? "Redirecting…" : "Continue with Google"}
          </button>
          <p className="muted mt-6 text-xs">
            You&apos;ll connect your Telegram account via phone number on the next step.
          </p>
        </div>
      </div>
    </main>
  );
}
