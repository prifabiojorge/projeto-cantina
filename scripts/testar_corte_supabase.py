"""Teste real isolado: cria somente seus proprios registros e remove ao terminar."""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sistema_cantina'))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')
os.environ['CANTINA_DATA_BACKEND'] = 'supabase'
os.environ['CANTINA_DISABLE_SCHEDULER'] = 'true'
os.environ['V2_AUTH_REQUIRED'] = 'true'

from app import create_app
import models
import cloud_models as cloud


def main():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    http = app.test_client()
    assert http.get('/dashboard').status_code == 302
    assert http.post('/api/checkin-portaria', json={'qrcode_hash':'teste'}).status_code == 401
    with http.session_transaction() as s:
        s['v2_access_token'] = 'teste-local'
        s['v2_user'] = {'papel':'admin','email':'teste-local'}
    for rota in ('/health','/dashboard','/alunos','/relatorio','/admin/configuracoes','/backup'):
        response = http.get(rota)
        assert response.status_code == 200, (rota, response.status_code)
        print('OK', rota)
    assert http.get('/health').json['backend'] == 'supabase'
    base = len(models.listar_alunos())
    matricula = 'TESTE-' + uuid.uuid4().hex
    aluno = models.cadastrar_aluno('Teste temporario integracao', matricula, '101', 'Integral')
    try:
        hash = aluno['qrcode_hash']
        assert http.get('/alunos/editar/'+aluno['id']).status_code == 200
        qr = http.get('/alunos/qrcode/'+matricula)
        assert qr.status_code == 200 and qr.data.startswith(b'\x89PNG')
        def scan(rota):
            r = http.post('/api/checkin-'+rota, json={'qrcode_hash':hash})
            assert r.status_code == 200
            return r.json['status']
        assert scan('cantina') == 'sem_checkin_portaria'
        assert scan('portaria') == 'ok'
        assert scan('portaria') == 'ja_registrado'
        assert scan('cantina') == 'ok'
        assert scan('cantina') == 'ja_almocou'
        diario = models.relatorio_detalhado_data(cloud.hoje())
        assert any(a['id']==aluno['id'] for a in diario['tabelas']['checkins_cantina'])
        models.desativar_aluno(aluno['id'])
        assert scan('portaria') == 'inativo'
        print('OK cadastro, UUID, QR, portaria, cantina, duplicidade, relatorio e inativo')
    finally:
        cloud.client().table('alunos').delete().eq('id',aluno['id']).execute()
    assert len(models.listar_alunos()) == base
    with http.session_transaction() as s:
        s['v2_user'] = {'papel':'portaria'}
    assert http.get('/backup').status_code == 403
    assert http.post('/api/checkin-cantina', json={'qrcode_hash':'teste'}).status_code == 403
    assert http.get('/portaria').status_code == 200
    print('OK permissoes e limpeza do registro temporario')


if __name__ == '__main__':
    main()
