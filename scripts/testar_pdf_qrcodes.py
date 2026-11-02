"""Verifica PDF em lote sem consultar ou alterar alunos reais."""
import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ['CANTINA_DISABLE_SCHEDULER'] = 'true'
os.environ['V2_AUTH_REQUIRED'] = 'false'
os.environ.pop('CANTINA_DATA_BACKEND', None)
os.environ.pop('VERCEL', None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sistema_cantina'))
from app import app, _legacy

alunos = [dict(nome='Aluno <Teste> & Nome longo para quebra de linha', matricula=f'TESTE-{i}',
               turma='101', qrcode_hash=f'qr-teste-{i}', ativo=True, id=i, turno='Integral') for i in range(293)]
with patch.object(_legacy, 'listar_alunos', return_value=alunos) as listar:
    http = app.test_client()
    pagina = http.get('/alunos')
    assert pagina.status_code == 200
    assert b'QR Codes em PDF' in pagina.data
    resposta = http.get('/alunos/qrcodes/pdf')
    assert resposta.status_code == 200, resposta.status_code
    assert resposta.mimetype == 'application/pdf'
    assert resposta.data.startswith(b'%PDF-')
    assert b'%%EOF' in resposta.data[-30:]
    assert 'attachment' in resposta.headers['Content-Disposition']
    listar.assert_called_with(ativo=True)
    print('OK: botao e PDF valido com 293 alunos ficticios, incluindo caracteres especiais.')
with patch.object(_legacy, 'listar_alunos', return_value=[]):
    assert app.test_client().get('/alunos/qrcodes/pdf').status_code == 302
    print('OK: lista vazia redireciona sem erro.')
