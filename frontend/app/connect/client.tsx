"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";

export function ConnectClient() {
  const router = useRouter();
  const [step, setStep] = useState<"phone" | "code" | "password">("phone");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [phoneCodeHash, setPhoneCodeHash] = useState("");
  const [tempSession, setTempSession] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendCode(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await apiPost<{ phone_code_hash: string; temp_session: string }>(
        "/tg/send-code",
        { phone }
      );
      setPhoneCodeHash(r.phone_code_hash);
      setTempSession(r.temp_session);
      setStep("code");
      toast.success("Code sent — check Telegram");
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function verifyCode(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await apiPost("/tg/verify-code", {
        phone,
        code,
        phone_code_hash: phoneCodeHash,
        temp_session: tempSession,
        password: password || null,
      });
      toast.success("Connected!");
      router.push("/channels");
    } catch (e: any) {
      const msg = String(e.message || "");
      if (msg.toLowerCase().includes("password") || msg.toLowerCase().includes("2fa")) {
        setStep("password");
        toast.message("Two-step verification needed — enter your Telegram password");
      } else {
        toast.error(msg);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel p-5 sm:p-6">
      <h1 className="text-xl font-bold sm:text-2xl">Connect Telegram</h1>
      <p className="muted mt-1 text-sm">
        Your session is encrypted at rest. We never store your password.
      </p>

      {step === "phone" && (
        <form onSubmit={sendCode} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm">Phone number (with country code)</label>
            <input
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+911234567890"
              className="input"
              autoFocus
            />
          </div>
          <button disabled={loading} className="btn-primary w-full">
            {loading ? "Sending…" : "Send code"}
          </button>
        </form>
      )}

      {step === "code" && (
        <form onSubmit={verifyCode} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm">OTP (from Telegram)</label>
            <input
              required
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="12345"
              className="input"
              autoFocus
            />
          </div>
          <button disabled={loading} className="btn-primary w-full">
            {loading ? "Verifying…" : "Verify"}
          </button>
          <button
            type="button"
            className="btn-ghost w-full"
            onClick={() => setStep("phone")}
          >
            Change number
          </button>
        </form>
      )}

      {step === "password" && (
        <form onSubmit={verifyCode} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm">Two-step password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              autoFocus
            />
          </div>
          <button disabled={loading} className="btn-primary w-full">
            {loading ? "Verifying…" : "Verify"}
          </button>
        </form>
      )}
    </div>
  );
}
