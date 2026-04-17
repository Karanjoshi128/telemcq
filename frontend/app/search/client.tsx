"use client";

import { Search } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { apiGet } from "@/lib/api";

type MCQ = {
  id: string;
  category: string | null;
  question: string;
  options: { key: string; text: string }[];
  correct_answer: string | null;
  selected_answer: string | null;
};

export function SearchClient() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<MCQ[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function run(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    try {
      const qs = new URLSearchParams({ page: "1", page_size: "30", q: q.trim() });
      const r = await apiGet<{ items: MCQ[] }>(`/mcqs?${qs.toString()}`);
      setResults(r.items);
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold sm:text-2xl">Search MCQs</h1>
      <form onSubmit={run} className="flex flex-col gap-2 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 muted" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="e.g. discovery layer OPAC"
            className="input pl-9"
          />
        </div>
        <button disabled={loading} className="btn-primary sm:w-auto">
          {loading ? "…" : "Search"}
        </button>
      </form>

      {results && results.length === 0 && (
        <div className="panel p-6 text-center muted">No matches.</div>
      )}

      <ul className="space-y-3">
        {results?.map((m) => (
          <li key={m.id} className="panel p-4 sm:p-5">
            {m.category && (
              <div className="mb-1 text-xs uppercase" style={{ color: "rgb(var(--accent))" }}>
                {m.category}
              </div>
            )}
            <div className="text-sm font-semibold sm:text-base">{m.question}</div>
            <ol className="mt-2 space-y-1 text-sm">
              {m.options.map((o) => {
                const isSelected = m.selected_answer === o.key;
                const isCorrect = m.correct_answer === o.key;
                const revealed = !!m.selected_answer;
                return (
                  <li
                    key={o.key}
                    className={`flex items-center gap-2 rounded px-2 py-1 ${
                      revealed && isCorrect ? "text-[rgb(var(--accent))] font-semibold" : ""
                    } ${revealed && isSelected && !isCorrect ? "text-red-500" : ""}`}
                  >
                    <span className="muted w-5 font-mono">{o.key}.</span>
                    <span>{o.text}</span>
                  </li>
                );
              })}
            </ol>
          </li>
        ))}
      </ul>
    </div>
  );
}
