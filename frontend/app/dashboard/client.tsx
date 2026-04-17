"use client";

import { Download, RefreshCw, Smartphone } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { apiDownload, apiGet, apiPost } from "@/lib/api";

type Status = {
  connected: boolean;
  phone: string | null;
  channel: { title: string; last_synced_at: string | null } | null;
};

type Stats = {
  total: number;
  answered: number;
  channel_title: string | null;
  last_synced_at: string | null;
};

export function DashboardClient() {
  const [status, setStatus] = useState<Status | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [exporting, setExporting] = useState(false);

  async function refresh() {
    try {
      const [s, st] = await Promise.all([
        apiGet<Status>("/tg/status"),
        apiGet<Stats>("/mcqs/stats"),
      ]);
      setStatus(s);
      setStats(st);
    } catch (e: any) {
      toast.error(e.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function syncNow() {
    setSyncing(true);
    try {
      const r = await apiPost<{ scraped: number }>("/scrape/me");
      toast.success(`Synced — ${r.scraped} new MCQs`);
      await refresh();
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSyncing(false);
    }
  }

  async function exportDocx() {
    setExporting(true);
    try {
      await apiDownload("/export/docx");
      toast.success("Download started");
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setExporting(false);
    }
  }

  if (!status) return <div className="muted">Loading…</div>;

  if (!status.connected) {
    return (
      <div className="panel p-8 text-center">
        <Smartphone className="mx-auto h-10 w-10 muted" />
        <h2 className="mt-4 text-2xl font-bold">Connect your Telegram</h2>
        <p className="muted mt-2">
          Log in with your phone number and the OTP Telegram sends to you.
        </p>
        <Link href="/connect" className="btn-primary mt-6">
          Connect Telegram
        </Link>
      </div>
    );
  }

  if (!status.channel) {
    return (
      <div className="panel p-8 text-center">
        <h2 className="text-2xl font-bold">Pick a channel</h2>
        <p className="muted mt-2">
          Choose one of the Telegram channels you&apos;ve joined.
        </p>
        <Link href="/channels" className="btn-primary mt-6">
          Browse channels
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="panel p-5 sm:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="muted text-xs uppercase tracking-wide">Channel</div>
            <div className="truncate text-lg font-semibold sm:text-xl">
              {status.channel.title}
            </div>
            <div className="muted mt-1 text-xs sm:text-sm">
              Last synced:{" "}
              {status.channel.last_synced_at
                ? new Date(status.channel.last_synced_at).toLocaleString()
                : "never"}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={syncNow}
              disabled={syncing}
              className="btn-ghost flex-1 sm:flex-initial"
            >
              <RefreshCw className={`h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
              {syncing ? "Syncing…" : "Sync now"}
            </button>
            <button
              onClick={exportDocx}
              disabled={exporting}
              className="btn-primary flex-1 sm:flex-initial"
            >
              <Download className="h-4 w-4" />
              {exporting ? "Exporting…" : "Export DOCX"}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3">
        <div className="panel p-4 sm:p-5">
          <div className="muted text-xs uppercase">Total MCQs</div>
          <div className="mt-1 text-2xl font-bold sm:text-3xl">{stats?.total ?? 0}</div>
        </div>
        <div className="panel p-4 sm:p-5">
          <div className="muted text-xs uppercase">Answered</div>
          <div className="mt-1 text-2xl font-bold sm:text-3xl">{stats?.answered ?? 0}</div>
        </div>
        <div className="panel col-span-2 p-4 sm:col-span-1 sm:p-5">
          <div className="muted text-xs uppercase">Phone</div>
          <div className="mt-1 truncate text-base font-semibold sm:text-lg">
            {status.phone}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Link href="/quiz" className="btn-primary flex-1 sm:flex-initial">
          Start practicing
        </Link>
        <Link href="/search" className="btn-ghost flex-1 sm:flex-initial">
          Search MCQs
        </Link>
      </div>
    </div>
  );
}
