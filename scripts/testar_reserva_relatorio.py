"""Verifica reserva diaria sem rede e somente com banco temporario."""
import os
import sqlite3
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

os.environ.pop('VERCEL', None)
os.environ.pop('CANTINA_DATA_BACKEND', None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sistema_cantina'))
import models
import cloud_models as cloud

pasta_testes = Path(__file__).resolve().parents[1] / 'instance'
pasta_testes.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=pasta_testes) as pasta:
    banco = str(Path(pasta) / 'teste.db')
    with sqlite3.connect(banco) as conn:
        conn.execute('''CREATE TABLE relatorios_enviados (
            id INTEGER PRIMARY KEY, data TEXT UNIQUE, total_esperado INTEGER,
            status TEXT, mensagem TEXT, enviado_em TEXT)''')
    conn.close()
    with patch.object(models, 'get_db', side_effect=lambda: sqlite3.connect(banco)):
        with ThreadPoolExecutor(max_workers=4) as executor:
            resultados = list(executor.map(models.reservar_envio_relatorio, [2] * 4))
        assert resultados.count(True) == 1, resultados
        assert not models.reservar_envio_relatorio(2)
        models.registrar_relatorio_enviado(2, status='falha')
        assert models.reservar_envio_relatorio(2)
        models.registrar_relatorio_enviado(2)
        assert not models.reservar_envio_relatorio(2)
        with sqlite3.connect(banco) as conn:
            conn.execute("UPDATE relatorios_enviados SET status='pendente'")
        conn.close()
        assert models.reservar_envio_relatorio(2)
print('OK SQLite: uma reserva simultanea, falha permite retry, enviado bloqueia e reabertura explicita funciona.')

cliente = MagicMock()
with patch.object(cloud, 'client', return_value=cliente), patch.object(cloud, 'rows', return_value=[]):
    assert cloud.reservar_envio_relatorio(2)
    payload = cliente.table.return_value.insert.call_args.args[0]
    assert payload['status'] == 'pendente' and payload['mensagem'] == 'Envio em andamento.'
    cliente.table.return_value.insert.return_value.execute.side_effect = cloud.APIError(
        {'code':'23505', 'message':'duplicate', 'hint':None, 'details':None})
    assert not cloud.reservar_envio_relatorio(2)

for registro in [
    {'status':'enviado'},
    {'status':'pendente', 'mensagem':'Envio em andamento.'},
]:
    with patch.object(cloud, 'rows', return_value=[registro]), patch.object(cloud, 'client') as conectar:
        assert not cloud.reservar_envio_relatorio(2)
        conectar.assert_not_called()

cliente = MagicMock()
registro = {'id':'teste', 'status':'falhou', 'updated_at':'2026-11-03T10:00:00+00:00'}
with patch.object(cloud, 'client', return_value=cliente), patch.object(cloud, 'rows', return_value=[registro]):
    consulta = cliente.table.return_value.update.return_value
    consulta.eq.return_value.eq.return_value.execute.return_value.data = [{'id':'teste'}]
    assert cloud.reservar_envio_relatorio(2)
    consulta.eq.assert_called_with('id', 'teste')
    consulta.eq.return_value.eq.assert_called_with('updated_at', registro['updated_at'])
    consulta.eq.return_value.eq.return_value.execute.return_value.data = []
    assert not cloud.reservar_envio_relatorio(2)
    consulta.eq.return_value.eq.return_value.execute.side_effect = cloud.APIError(
        {'code':'42501', 'message':'permission denied', 'hint':None, 'details':None})
    with TestCase().assertRaises(cloud.APIError):
        cloud.reservar_envio_relatorio(2)
print('OK Supabase simulado: conflito unico, bloqueio de pendente/enviado e atualizacao condicionada a versao do registro.')
