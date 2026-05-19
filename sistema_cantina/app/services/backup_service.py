from __future__ import annotations

from datetime import datetime
import json


def backup_filename(prefix: str = "cantina") -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_backup_{stamp}.json"


def serialize_backup(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
