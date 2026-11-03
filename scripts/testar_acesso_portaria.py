"""Verifica acesso publico da portaria sem rede nem gravacoes de check-in."""
import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ['CANTINA_DISABLE_SCHEDULER'] = 'true'
os.environ['V2_AUTH_REQUIRED'] = 'true'
os.environ.pop('CANTINA_DATA_BACKEND', None)
os.environ.pop('VERCEL', None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sistema_cantina'))
with patch('database.init_db'):
    from app import app, _legacy

app.config['TESTING'] = True
http = app.test_client()
resposta = http.get('/portaria')
assert resposta.status_code == 200
assert b'btn-start' in resposta.data
assert b'id="btn-enviar-whatsapp"' not in resposta.data
with patch.object(_legacy, 'registrar_checkin_portaria', return_value={'status':'ok', 'aluno':None}) as registrar:
    resposta = http.post('/api/checkin-portaria', json={'qrcode_hash':'teste-sem-gravar'})
    assert resposta.status_code == 200 and resposta.json['status'] == 'ok'
    registrar.assert_called_once_with('teste-sem-gravar')
    assert http.post('/api/checkin-portaria', json={}).status_code == 400
    assert registrar.call_count == 1
with patch.object(_legacy, 'contar_checkins_portaria_hoje', return_value=4):
    assert http.get('/api/portaria/contagem-hoje').json['total'] == 4
for rota in ('/dashboard', '/alunos', '/backup'):
    assert http.get(rota).status_code == 302
for rota in ('/api/whatsapp/teste', '/api/relatorio/gerar-agora'):
    assert http.post(rota).status_code == 302
assert http.get('/cantina').status_code == 302
assert http.post('/api/checkin-cantina', json={'qrcode_hash':'teste'}).status_code == 401
with http.session_transaction() as sessao:
    sessao['v2_access_token'] = 'teste-local'
    sessao['v2_user'] = {'papel':'portaria'}
assert http.get('/portaria').status_code == 200
assert http.get('/backup').status_code == 403
assert http.post('/api/relatorio/gerar-agora').status_code == 403
with http.session_transaction() as sessao:
    sessao['v2_user'] = {'papel':'admin'}
assert b'id="btn-enviar-whatsapp"' in http.get('/portaria').data
print('OK: portaria e check-in publicos; WhatsApp, administracao e cantina protegidos.')
