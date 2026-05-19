from __future__ import annotations

from typing import Any

from ..supabase_client import get_supabase_admin


class SupabaseRepository:
    table_name: str

    def __init__(self, client: Any | None = None):
        self.client = client or get_supabase_admin()

    @property
    def table(self):
        return self.client.table(self.table_name)
