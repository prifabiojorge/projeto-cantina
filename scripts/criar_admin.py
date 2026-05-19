#!/usr/bin/env python3
"""Cria ou atualiza o perfil administrativo no Supabase.

Por segurança, crie o usuário primeiro no painel Supabase Auth. Depois rode:

  set AUTH_USER_ID=<uuid-do-usuario>
  python scripts/criar_admin.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    _load_env()
    user_id = os.environ.get("AUTH_USER_ID", "").strip()
    nome = os.environ.get("AUTH_USER_NAME", "Administrador").strip()
    papel = os.environ.get("AUTH_USER_ROLE", "admin").strip()

    if not user_id:
        print("Defina AUTH_USER_ID com o UUID do usuário criado no Supabase Auth.")
        return 1

    client = _client()
    client.table("perfis_usuarios").upsert(
        {
            "user_id": user_id,
            "nome": nome,
            "papel": papel,
            "ativo": True,
        },
        on_conflict="user_id",
    ).execute()
    print(f"Perfil {papel} criado/atualizado para {user_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
