#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:  # pragma: no cover - depends on runtime env
    Fernet = None  # type: ignore[assignment]
    InvalidToken = Exception  # type: ignore[assignment]
    PBKDF2HMAC = None  # type: ignore[assignment]
    hashes = None  # type: ignore[assignment]


@dataclass(frozen=True)
class SecureProfileStore:
    enabled: bool
    storage_dir: str
    master_key: str

    def _profile_path(self, scope: str, profile_id: str) -> Path:
        if scope not in {"user", "server"}:
            raise ValueError("scope must be 'user' or 'server'")
        safe_id = "".join(ch for ch in profile_id if ch.isalnum() or ch in {"-", "_", "."}) or "default"
        return Path(self.storage_dir) / scope / f"{safe_id}.enc.json"

    def _derive_fernet(self, salt: bytes):
        if Fernet is None or PBKDF2HMAC is None or hashes is None:
            raise RuntimeError("cryptography package is required for secure profile storage")
        if not self.master_key:
            raise RuntimeError("AXXON_SECURE_PROFILE_MASTER_KEY is required when secure profile storage is enabled")
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200000)
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode("utf-8")))
        return Fernet(key)

    def save_profile(self, scope: str, profile_id: str, payload: dict) -> str:
        if not self.enabled:
            raise RuntimeError("secure profile storage is disabled")

        out = self._profile_path(scope, profile_id)
        out.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(out.parent, 0o700)
        except OSError:
            pass

        salt = os.urandom(16)
        f = self._derive_fernet(salt)
        token = f.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("utf-8")
        envelope = {
            "v": 1,
            "alg": "fernet+pbkdf2_sha256",
            "salt_b64": base64.b64encode(salt).decode("ascii"),
            "token": token,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        out.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            os.chmod(out, 0o600)
        except OSError:
            pass
        return str(out)

    def load_profile(self, scope: str, profile_id: str) -> dict | None:
        if not self.enabled:
            return None

        src = self._profile_path(scope, profile_id)
        if not src.exists():
            return None

        envelope = json.loads(src.read_text(encoding="utf-8"))
        salt = base64.b64decode(envelope["salt_b64"])
        token = envelope["token"].encode("utf-8")
        f = self._derive_fernet(salt)
        try:
            raw = f.decrypt(token).decode("utf-8")
        except InvalidToken as ex:
            raise RuntimeError("Failed to decrypt secure profile (wrong key or corrupted file)") from ex
        return json.loads(raw)
