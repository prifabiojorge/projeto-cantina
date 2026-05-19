from __future__ import annotations

from .base import SupabaseRepository


class ConfiguracoesRepository(SupabaseRepository):
    table_name = "configuracoes"

    def upsert_many(self, rows: list[dict]):
        if not rows:
            return []
        return self.table.upsert(rows, on_conflict="chave").execute().data or []
