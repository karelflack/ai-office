"""
Envelope encryption for API keys (magnus compliance item C1).

Scheme:
- Generate a cryptographically random 32-byte raw key
- Encrypt with AES-256-GCM using the application encryption key from settings
- Store: base64(iv + tag + ciphertext)
- Lookup: SHA-256 hash of the raw key (stored in key_hash column)
- Display: last 6 chars of raw key hex (key_preview, shown as sk-...abc123)

The application ENCRYPTION_KEY must be a 32-byte hex string (64 hex chars).
Generate with: openssl rand -hex 32
"""

import base64
import hashlib
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


def _get_aes_key() -> bytes:
    """Decode the hex-encoded encryption key from settings."""
    raw = bytes.fromhex(settings.encryption_key)
    if len(raw) != 32:
        raise ValueError("ENCRYPTION_KEY must be a 32-byte hex string (64 hex chars)")
    return raw


def generate_api_key() -> tuple[str, str, str, str]:
    """
    Generate a new API key.

    Returns:
        raw_key: the full plaintext key string (shown to user once, never stored)
        key_hash: hex SHA-256 of raw_key (stored in DB for lookup)
        key_encrypted: base64(iv + tag + ciphertext) stored in DB
        key_preview: last 6 chars of raw_key for masked display (sk-...abc123)
    """
    raw_bytes = secrets.token_bytes(32)
    raw_key = "sk-" + raw_bytes.hex()  # 67-char string, e.g. sk-<64hexchars>

    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    aes_key = _get_aes_key()
    aesgcm = AESGCM(aes_key)
    iv = os.urandom(12)  # 96-bit IV for GCM
    ciphertext = aesgcm.encrypt(iv, raw_key.encode(), None)
    # ciphertext from AESGCM includes the 16-byte GCM tag appended
    key_encrypted = base64.b64encode(iv + ciphertext).decode()

    key_preview = raw_key[-6:]  # last 6 chars

    return raw_key, key_hash, key_encrypted, key_preview


def decrypt_api_key(key_encrypted: str) -> str:
    """Decrypt an API key from its stored encrypted form. Used only at creation response."""
    aes_key = _get_aes_key()
    aesgcm = AESGCM(aes_key)
    raw = base64.b64decode(key_encrypted)
    iv = raw[:12]
    ciphertext = raw[12:]
    return aesgcm.decrypt(iv, ciphertext, None).decode()


def hash_api_key(raw_key: str) -> str:
    """Hash an incoming API key for database lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()
