from __future__ import annotations

from ..repositories.configuracoes_repository import ConfiguracoesRepository


class ConfigService:
    def __init__(self, repository: ConfiguracoesRepository | None = None):
        self.repository = repository or ConfiguracoesRepository()

    def upsert_many(self, rows: list[dict]):
        return self.repository.upsert_many(rows)
