"use client";

import { Check, ChevronLeft, ChevronRight, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";

type MCQ = {
  id: string;
  category: string | null;
  question: string;
  options: { key: string; text: string }[];
  correct_answer: string | null;
  source_date: string;
  selected_answer: string | null;
};

type List = { items: MCQ[]; total: number; page: number; page_size: number };

const PAGE_SIZE = 10;

export function QuizClient({ initialQuery = "" }: { initialQuery?: string }) {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<List | null>(null);
  const [local, setLocal] = useState<Record<string, string>>({}); // unsaved selections
  const [submittedOnce, setSubmittedOnce] = useState<Record<string, true>>({});
  const [submitting, setSubmitting] = useState(false);
  const [q] = useState(initialQuery);

  async function load(p: number) {
    setData(null);
    try {
      const qs = new URLSearchParams({ page: String(p), page_size: String(PAGE_SIZE) });
      if (q) qs.set("q", q);
      const r = await apiGet<List>(`/mcqs?${qs.toString()}`);
      setData(r);
      // seed local state with persisted answers for this page
      const seed: Record<string, string> = {};
      const subseed: Record<string, true> = {};
      r.items.forEach((m) => {
        if (m.selected_answer) {
          seed[m.id] = m.selected_answer;
          subseed[m.id] = true;
        }
      });
      setLocal(seed);
      setSubmittedOnce(subseed);
    } catch (e: any) {
      toast.error(e.message);
    }
  }

  useEffect(() => {
    load(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const totalPages = useMemo(
    () => (data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1),
    [data]
  );

  async function submit() {
    if (!data) return;
    const toSave: Record<string, string> = {};
    data.items.forEach((m) => {
      if (local[m.id]) toSave[m.id] = local[m.id];
    });
    if (Object.keys(toSave).length === 0) {
      toast.message("Pick at least one answer first");
      return;
    }
    setSubmitting(true);
    try {
      await apiPost("/mcqs/answers", { answers: toSave });
      toast.success("Saved");
      const next: Record<string, true> = { ...submittedOnce };
      Object.keys(toSave).forEach((id) => (next[id] = true));
      setSubmittedOnce(next);
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!data) return <div className="muted">Loading…</div>;
  if (data.total === 0)
    return (
      <div className="panel p-8 text-center">
        No MCQs yet — run a sync from the dashboard.
      </div>
    );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold sm:text-2xl">Practice</h1>
          <div className="muted text-sm">
            {data.total} total · page {data.page} of {totalPages}
          </div>
        </div>
        <button onClick={submit} disabled={submitting} className="btn-primary">
          {submitting ? "Saving…" : "Submit"}
        </button>
      </div>

      <ol className="space-y-4">
        {data.items.map((m, idx) => {
          const num = (data.page - 1) * data.page_size + idx + 1;
          const selected = local[m.id];
          const revealed = !!submittedOnce[m.id] && !!selected;
          return (
            <li key={m.id} className="panel p-4 sm:p-5">
              {m.category && (
                <div className="mb-2 text-xs font-semibold uppercase" style={{ color: "rgb(var(--accent))" }}>
                  {m.category}
                </div>
              )}
              <div className="text-sm font-semibold sm:text-base">
                Q{num}. {m.question}
              </div>
              <div className="mt-3 space-y-2">
                {m.options.map((o) => {
                  const isSelected = selected === o.key;
                  const isCorrect = m.correct_answer === o.key;
                  const wrong = revealed && isSelected && !isCorrect;
                  const good = revealed && isCorrect;
                  return (
                    <label
                      key={o.key}
                      className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 text-sm transition-colors hairline ${
                        good ? "border-[rgb(var(--accent))]" : ""
                      } ${wrong ? "border-red-500/60" : ""}`}
                      style={
                        good
                          ? { background: "rgba(0,220,130,0.08)" }
                          : wrong
                          ? { background: "rgba(239,68,68,0.08)" }
                          : undefined
                      }
                    >
                      <input
                        type="radio"
                        name={`q_${m.id}`}
                        checked={isSelected}
                        onChange={() => setLocal((s) => ({ ...s, [m.id]: o.key }))}
                        className="h-4 w-4"
                      />
                      <span className="muted w-5 font-mono">{o.key}.</span>
                      <span className="flex-1">{o.text}</span>
                      {good && <Check className="h-4 w-4" style={{ color: "rgb(var(--accent))" }} />}
                      {wrong && <X className="h-4 w-4 text-red-500" />}
                    </label>
                  );
                })}
              </div>
              {revealed && m.correct_answer && selected !== m.correct_answer && (
                <div className="muted mt-2 text-xs">
                  Correct answer: {m.correct_answer}
                </div>
              )}
            </li>
          );
        })}
      </ol>

      <div className="flex items-center justify-between gap-2">
        <button
          className="btn-ghost"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
        >
          <ChevronLeft className="h-4 w-4" /> <span className="hidden sm:inline">Prev</span>
        </button>
        <div className="muted text-xs sm:text-sm">
          Page {page} / {totalPages}
        </div>
        <button
          className="btn-ghost"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          <span className="hidden sm:inline">Next</span> <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
