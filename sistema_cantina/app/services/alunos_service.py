from __future__ import annotations

from ..repositories.alunos_repository import AlunosRepository


class AlunosService:
    def __init__(self, repository: AlunosRepository | None = None):
        self.repository = repository or AlunosRepository()

    def listar_ativos(self):
        return self.repository.listar(ativo=True)
