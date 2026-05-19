from __future__ import annotations

from datetime import date

from ..repositories.alunos_repository import AlunosRepository
from ..repositories.checkins_repository import (
    CheckinsCantinaRepository,
    CheckinsPortariaRepository,
)


class CheckinService:
    def __init__(
        self,
        alunos: AlunosRepository | None = None,
        portaria: CheckinsPortariaRepository | None = None,
        cantina: CheckinsCantinaRepository | None = None,
    ):
        self.alunos = alunos or AlunosRepository()
        self.portaria = portaria or CheckinsPortariaRepository()
        self.cantina = cantina or CheckinsCantinaRepository()

    def registrar_portaria(self, qrcode_hash: str, data_iso: str | None = None):
        aluno = self.alunos.buscar_por_hash(qrcode_hash)
        if not aluno:
            return {"status": "nao_encontrado", "aluno": None}
        if not aluno.get("ativo", True):
            return {"status": "inativo", "aluno": aluno}
        payload = {"aluno_id": aluno["id"], "data": data_iso or date.today().isoformat()}
        self.portaria.inserir(payload)
        return {"status": "ok", "aluno": aluno}

    def registrar_cantina(self, qrcode_hash: str, data_iso: str | None = None):
        aluno = self.alunos.buscar_por_hash(qrcode_hash)
        if not aluno:
            return {"status": "nao_encontrado", "aluno": None}
        if not aluno.get("ativo", True):
            return {"status": "inativo", "aluno": aluno}
        payload = {"aluno_id": aluno["id"], "data": data_iso or date.today().isoformat()}
        self.cantina.inserir(payload)
        return {"status": "ok", "aluno": aluno}
