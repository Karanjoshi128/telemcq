import hmac

import httpx
import jwt
from fastapi import HTTPException, Request, status

from .config import get_settings


def _verify_locally(token: str, secret: str) -> str | None:
    """Try HS256 verification with the legacy JWT secret. Returns sub if OK."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None


def _verify_via_supabase(token: str) -> str | None:
    """Fallback: ask Supabase to resolve the token (works for ES256 / RS256)."""
    s = get_settings()
    try:
        r = httpx.get(
            f"{s.SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": s.SUPABASE_SERVICE_ROLE_KEY,
            },
            timeout=5.0,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get("id")
    except httpx.HTTPError:
        return None


def current_user_id(request: Request) -> str:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = auth.split(" ", 1)[1]

    s = get_settings()
    uid = _verify_locally(token, s.SUPABASE_JWT_SECRET) or _verify_via_supabase(token)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return uid


def require_cron_secret(request: Request) -> None:
    s = get_settings()
    provided = request.headers.get("x-cron-secret") or ""
    if not hmac.compare_digest(provided, s.CRON_SECRET):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad cron secret")
