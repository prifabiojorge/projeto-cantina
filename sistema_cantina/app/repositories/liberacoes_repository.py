from __future__ import annotations

from .base import SupabaseRepository


class LiberacoesRepository(SupabaseRepository):
    table_name = "liberacoes_forcadas"

    def inserir(self, aluno_id: str, motivo: str, data: str | None = None):
        payload = {"aluno_id": aluno_id, "motivo": motivo}
        if data:
            payload["data"] = data
        return self.table.insert(payload).execute().data
