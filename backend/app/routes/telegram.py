import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from ..core import ratelimit
from ..core.crypto import decrypt, encrypt
from ..core.deps import current_user_id
from ..core.supabase import service_client
from ..tg import auth as tg_auth
from ..tg import channels as tg_channels

log = logging.getLogger(__name__)
router = APIRouter(prefix="/tg", tags=["telegram"])

PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")


class SendCodeIn(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, v: str) -> str:
        v = v.strip().replace(" ", "").replace("-", "")
        if not PHONE_RE.match(v):
            raise ValueError("Phone must be digits (with optional leading +), 7-15 chars")
        return v


class SendCodeOut(BaseModel):
    phone_code_hash: str
    temp_session: str


@router.post("/send-code", response_model=SendCodeOut)
async def send_code(body: SendCodeIn, user_id: str = Depends(current_user_id)):
    ratelimit.check(user_id, "send-code", limit=5, window_seconds=600)
    try:
        data = await tg_auth.send_code(body.phone)
    except Exception:
        log.exception("send_code failed")
        raise HTTPException(400, "Failed to send code. Check the phone number and try again.")
    return SendCodeOut(**data)


class VerifyCodeIn(BaseModel):
    phone: str
    code: str
    phone_code_hash: str
    temp_session: str
    password: str | None = None

    @field_validator("code")
    @classmethod
    def valid_code(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or not (4 <= len(v) <= 8):
            raise ValueError("Code must be 4-8 digits")
        return v


@router.post("/verify-code")
async def verify_code(body: VerifyCodeIn, user_id: str = Depends(current_user_id)):
    ratelimit.check(user_id, "verify-code", limit=10, window_seconds=600)
    try:
        session_str = await tg_auth.verify_code(
            body.phone, body.code, body.phone_code_hash, body.temp_session, body.password
        )
    except Exception as e:
        msg = str(e).lower()
        log.exception("verify_code failed")
        # Surface known user-facing cases; mask internals otherwise.
        if "password" in msg or "2fa" in msg:
            raise HTTPException(400, "Two-step verification password required")
        if "code" in msg and ("invalid" in msg or "expired" in msg):
            raise HTTPException(400, "Invalid or expired code")
        raise HTTPException(400, "Verification failed")

    enc = encrypt(session_str)
    sb = service_client()
    sb.table("telegram_accounts").upsert({
        "user_id": user_id,
        "phone": body.phone,
        "session_encrypted": enc,
    }).execute()
    return {"ok": True}


@router.get("/channels")
async def list_channels(user_id: str = Depends(current_user_id)):
    sb = service_client()
    res = sb.table("telegram_accounts").select("session_encrypted").eq("user_id", user_id).single().execute()
    if not res.data:
        raise HTTPException(400, "Telegram account not connected")
    session_str = decrypt(res.data["session_encrypted"])
    try:
        chans = await tg_channels.list_channels(session_str)
    except Exception:
        log.exception("list_channels failed")
        raise HTTPException(400, "Failed to load channels")
    return {"channels": chans}


class SelectChannelIn(BaseModel):
    tg_channel_id: int
    tg_access_hash: int | None = None
    title: str


@router.post("/channels/select")
async def select_channel(body: SelectChannelIn, user_id: str = Depends(current_user_id)):
    sb = service_client()
    # v1: one channel per user -> delete existing then insert
    sb.table("channels").delete().eq("user_id", user_id).execute()
    sb.table("channels").insert({
        "user_id": user_id,
        "tg_channel_id": body.tg_channel_id,
        "tg_access_hash": body.tg_access_hash,
        "title": body.title,
    }).execute()
    return {"ok": True}


@router.get("/status")
async def status(user_id: str = Depends(current_user_id)):
    sb = service_client()
    acct = sb.table("telegram_accounts").select("phone, connected_at").eq("user_id", user_id).execute()
    ch = sb.table("channels").select("*").eq("user_id", user_id).execute()
    return {
        "connected": bool(acct.data),
        "phone": acct.data[0]["phone"] if acct.data else None,
        "channel": ch.data[0] if ch.data else None,
    }


@router.post("/disconnect")
async def disconnect(user_id: str = Depends(current_user_id)):
    sb = service_client()
    sb.table("telegram_accounts").delete().eq("user_id", user_id).execute()
    sb.table("channels").delete().eq("user_id", user_id).execute()
    return {"ok": True}
