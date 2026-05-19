from __future__ import annotations

from datetime import date

from ..repositories.relatorios_repository import RelatoriosRepository


class RelatorioService:
    def __init__(self, repository: RelatoriosRepository | None = None):
        self.repository = repository or RelatoriosRepository()

    def registrar_falha_envio(self, mensagem: str, total_esperado: int = 0, data_iso: str | None = None):
        return self.repository.registrar_status(
            data_iso or date.today().isoformat(),
            total_esperado,
            "falhou",
            mensagem,
        )
