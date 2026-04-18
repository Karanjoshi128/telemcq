"use client";

import { Download, X } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { apiDownload } from "@/lib/api";

type Props = {
  open: boolean;
  onClose: () => void;
  total: number;
};

export function ExportModal({ open, onClose, total }: Props) {
  const [start, setStart] = useState(1);
  const [end, setEnd] = useState(total);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setStart(1);
      setEnd(total);
    }
  }, [open, total]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const invalid = start < 1 || end < 1 || start > end || end > total;

  async function download(s: number, e: number) {
    setBusy(true);
    try {
      await apiDownload(`/export/docx?start=${s}&end=${e}`);
      toast.success("Download started");
      onClose();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (invalid) return;
    await download(start, end);
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="panel w-full max-w-md p-5 sm:p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold sm:text-xl">Export to DOCX</h2>
          <button
            onClick={onClose}
            className="btn-ghost h-8 w-8 !p-0"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="muted mt-1 text-sm">
          Choose a range of questions to include. Total: <b>{total}</b>
        </p>

        <form onSubmit={submit} className="mt-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs uppercase muted">From Q</label>
              <input
                type="number"
                min={1}
                max={total}
                value={start}
                onChange={(e) => setStart(parseInt(e.target.value) || 1)}
                className="input"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase muted">To Q</label>
              <input
                type="number"
                min={1}
                max={total}
                value={end}
                onChange={(e) => setEnd(parseInt(e.target.value) || total)}
                className="input"
              />
            </div>
          </div>

          {invalid && (
            <div className="text-xs text-red-500">
              Range must be between 1 and {total}, and start ≤ end.
            </div>
          )}

          <div className="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              onClick={() => download(1, total)}
              disabled={busy || total === 0}
              className="btn-ghost flex-1"
            >
              All ({total})
            </button>
            <button
              type="submit"
              disabled={busy || invalid}
              className="btn-primary flex-1"
            >
              <Download className="h-4 w-4" />
              {busy ? "Downloading…" : "Download range"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
