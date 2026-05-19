from __future__ import annotations

from .base import SupabaseRepository


class UsuariosRepository(SupabaseRepository):
    table_name = "perfis_usuarios"

    def upsert_perfil(self, user_id: str, papel: str = "admin", nome: str | None = None):
        payload = {"user_id": user_id, "papel": papel, "nome": nome, "ativo": True}
        return self.table.upsert(payload, on_conflict="user_id").execute().data
