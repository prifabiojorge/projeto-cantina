from __future__ import annotations

from .base import SupabaseRepository


class RelatoriosRepository(SupabaseRepository):
    table_name = "relatorios_enviados"

    def registrar_status(self, data: str, total_esperado: int, status: str, mensagem: str):
        payload = {
            "data": data,
            "total_esperado": total_esperado,
            "status": status,
            "mensagem": mensagem,
        }
        return self.table.upsert(payload, on_conflict="data").execute().data
