from __future__ import annotations

from .base import SupabaseRepository


class CheckinsPortariaRepository(SupabaseRepository):
    table_name = "checkin_portaria"

    def inserir(self, payload: dict):
        return self.table.insert(payload).execute().data


class CheckinsCantinaRepository(SupabaseRepository):
    table_name = "checkin_cantina"

    def inserir(self, payload: dict):
        return self.table.insert(payload).execute().data
