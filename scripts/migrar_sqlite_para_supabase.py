#!/usr/bin/env python3
"""Migra dados do SQLite legado para o Supabase/Postgres.

Uso:
  python scripts/migrar_sqlite_para_supabase.py

Requer:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
"""

from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import sys


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "sistema_cantina" / "cantina.db"


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
        raise SystemExit("Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente.")
    return create_client(url, key)


def _rows(conn: sqlite3.Connection, sql: str):
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql).fetchall()]


def alunos_payload(conn: sqlite3.Connection) -> list[dict]:
    alunos = _rows(conn, "SELECT * FROM alunos ORDER BY id")
    return [
        {
            "legacy_id": aluno["id"],
            "nome": aluno["nome"],
            "matricula": aluno["matricula"],
            "turma": aluno["turma"],
            "turno": aluno["turno"],
            "qrcode_hash": aluno["qrcode_hash"],
            "ativo": bool(aluno["ativo"]),
            "criado_em": aluno["criado_em"],
        }
        for aluno in alunos
    ]


def sync_alunos(client, conn: sqlite3.Connection) -> dict[int, str]:
    payload = alunos_payload(conn)
    if payload:
        client.table("alunos").upsert(payload, on_conflict="matricula").execute()

    rows = client.table("alunos").select("id,legacy_id").execute().data or []
    return {int(row["legacy_id"]): row["id"] for row in rows if row.get("legacy_id") is not None}


def sync_checkins(client, conn: sqlite3.Connection, id_map: dict[int, str]) -> None:
    portaria = _rows(conn, "SELECT * FROM checkin_portaria ORDER BY id")
    cantina = _rows(conn, "SELECT * FROM checkin_cantina ORDER BY id")

    portaria_payload = [
        {
            "aluno_id": id_map[row["aluno_id"]],
            "data": row["data"],
            "hora_checkin": row["hora_checkin"],
            "origem": "migracao_sqlite",
        }
        for row in portaria
        if row["aluno_id"] in id_map
    ]
    cantina_payload = [
        {
            "aluno_id": id_map[row["aluno_id"]],
            "data": row["data"],
            "hora_almoco": row["hora_almoco"],
            "origem": "migracao_sqlite",
        }
        for row in cantina
        if row["aluno_id"] in id_map
    ]

    if portaria_payload:
        client.table("checkin_portaria").upsert(
            portaria_payload, on_conflict="aluno_id,data"
        ).execute()
    if cantina_payload:
        client.table("checkin_cantina").upsert(
            cantina_payload, on_conflict="aluno_id,data"
        ).execute()


def sync_configuracoes(client, conn: sqlite3.Connection) -> None:
    rows = _rows(conn, "SELECT chave, valor, descricao, atualizado_em FROM configuracoes")
    if rows:
        client.table("configuracoes").upsert(rows, on_conflict="chave").execute()


def main() -> int:
    if not DB_PATH.exists():
        print(f"Banco SQLite não encontrado: {DB_PATH}")
        return 1

    client = _client()
    conn = sqlite3.connect(DB_PATH)
    try:
        id_map = sync_alunos(client, conn)
        sync_checkins(client, conn, id_map)
        sync_configuracoes(client, conn)
    finally:
        conn.close()

    print(f"Migração concluída. Alunos mapeados: {len(id_map)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
