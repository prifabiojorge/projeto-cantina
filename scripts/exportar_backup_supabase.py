#!/usr/bin/env python3
"""Exporta backup lógico do Supabase para JSON local."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import os
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups"
TABLES = [
    "alunos",
    "checkin_portaria",
    "checkin_cantina",
    "liberacoes_forcadas",
    "relatorios_enviados",
    "configuracoes",
    "perfis_usuarios",
]


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv(ROOT / ".env")


def _client():
    _load_env()
    try:
        from supabase import create_client  # type: ignore
    except Exception as exc:
        raise SystemExit("Instale as dependências: pip install -r requirements.txt") from exc

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise SystemExit("Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY.")
    return create_client(url, key)


def main() -> int:
    client = _client()
    BACKUP_DIR.mkdir(exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tables": {},
    }
    for table in TABLES:
        payload["tables"][table] = client.table(table).select("*").execute().data or []

    path = BACKUP_DIR / f"cantina_supabase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Backup exportado: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
