import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <header className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <div className="flex items-center gap-2 font-semibold">
          <span className="inline-block h-3 w-3 rounded-full" style={{ background: "rgb(var(--accent))" }} />
          TeleMCQ
        </div>
        <ThemeToggle />
      </header>

      <section className="mx-auto max-w-3xl px-4 py-16 text-center sm:py-24">
        <h1 className="text-3xl font-bold tracking-tight sm:text-5xl">
          Turn your Telegram MCQ channel<br className="hidden sm:inline" />{" "}
          <span style={{ color: "rgb(var(--accent))" }}>into a practice notebook.</span>
        </h1>
        <p className="muted mx-auto mt-5 max-w-xl text-base sm:mt-6 sm:text-lg">
          Connect your Telegram account, pick a channel, and TeleMCQ quietly
          scrapes every quiz into a searchable, paginated practice set. Export
          to Word anytime.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:mt-10">
          <Link href="/login" className="btn-primary">Get started</Link>
          <a href="https://github.com" className="btn-ghost">Source</a>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl grid-cols-1 gap-4 px-4 pb-16 sm:pb-24 md:grid-cols-3">
        {[
          ["Google sign-in", "One click with your Google account."],
          ["Telegram OTP", "Connect your own Telegram via phone + code."],
          ["Word export", "Clean .docx with answers you selected."],
        ].map(([t, d]) => (
          <div key={t} className="panel p-5">
            <div className="font-semibold">{t}</div>
            <div className="muted mt-1 text-sm">{d}</div>
          </div>
        ))}
      </section>
    </main>
  );
}
