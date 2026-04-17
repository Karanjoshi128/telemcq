import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .config import get_settings


def _key() -> bytes:
    raw = base64.b64decode(get_settings().SESSION_ENCRYPTION_KEY)
    if len(raw) != 32:
        raise ValueError("SESSION_ENCRYPTION_KEY must decode to 32 bytes")
    return raw


def encrypt(plaintext: str) -> str:
    aes = AESGCM(_key())
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")


def decrypt(token: str) -> str:
    data = base64.b64decode(token)
    nonce, ct = data[:12], data[12:]
    aes = AESGCM(_key())
    return aes.decrypt(nonce, ct, None).decode("utf-8")
