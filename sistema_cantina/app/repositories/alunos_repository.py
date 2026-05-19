from __future__ import annotations

from .base import SupabaseRepository


class AlunosRepository(SupabaseRepository):
    table_name = "alunos"

    def listar(self, ativo: bool | None = None):
        query = self.table.select("*").order("turma").order("nome")
        if ativo is not None:
            query = query.eq("ativo", ativo)
        return query.execute().data or []

    def buscar_por_hash(self, qrcode_hash: str):
        result = self.table.select("*").eq("qrcode_hash", qrcode_hash).limit(1).execute()
        rows = result.data or []
        return rows[0] if rows else None

    def upsert_many(self, alunos: list[dict]):
        if not alunos:
            return []
        return self.table.upsert(alunos, on_conflict="matricula").execute().data or []
