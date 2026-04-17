"use client";

import { Hash } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";

type Channel = {
  tg_channel_id: number;
  tg_access_hash: number | null;
  title: string;
  username: string | null;
  is_broadcast: boolean;
};

export function ChannelsClient() {
  const router = useRouter();
  const [channels, setChannels] = useState<Channel[] | null>(null);
  const [selecting, setSelecting] = useState<number | null>(null);

  useEffect(() => {
    apiGet<{ channels: Channel[] }>("/tg/channels")
      .then((r) => setChannels(r.channels))
      .catch((e) => toast.error(e.message));
  }, []);

  async function select(c: Channel) {
    setSelecting(c.tg_channel_id);
    try {
      await apiPost("/tg/channels/select", {
        tg_channel_id: c.tg_channel_id,
        tg_access_hash: c.tg_access_hash,
        title: c.title,
      });
      toast.success(`Selected ${c.title}`);
      router.push("/dashboard");
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSelecting(null);
    }
  }

  if (!channels) return <div className="muted">Loading channels…</div>;
  if (channels.length === 0)
    return (
      <div className="panel p-8 text-center">
        You haven&apos;t joined any channels yet. Join the MCQ channel in
        Telegram, then refresh.
      </div>
    );

  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold sm:text-2xl">Select a channel</h1>
      <p className="muted text-sm">Only one channel per account in this version.</p>
      <ul className="mt-4 space-y-2">
        {channels.map((c) => (
          <li key={c.tg_channel_id}>
            <button
              onClick={() => select(c)}
              disabled={selecting !== null}
              className="panel flex w-full items-center gap-3 p-3 text-left hover:border-[rgb(var(--accent))] sm:p-4"
            >
              <Hash className="h-5 w-5 shrink-0 muted" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold sm:text-base">{c.title}</div>
                <div className="muted truncate text-xs">
                  {c.username ? `@${c.username}` : "private"} ·{" "}
                  {c.is_broadcast ? "channel" : "group"}
                </div>
              </div>
              {selecting === c.tg_channel_id && <span className="muted text-sm">…</span>}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
