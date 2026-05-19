#!/usr/bin/env python3
"""
Testes das funcionalidades do Prompt 6:
- Exportação de relatórios (CSV/PDF)
- Impressão em lote de QR codes
- Tela de configurações
- Sistema de backup
"""
import sys
import os
sys.path.insert(0, '.')

from app import app
import tempfile
import io

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

def test_imprimir_qrcodes():
    """Testa a página de impressão de QR codes."""
    with app.test_client() as client:
        resp = client.get('/alunos/imprimir-qrcodes')
        assert resp.status_code == 200, f'Rota QR codes retornou {resp.status_code}'
        html = resp.get_data(as_text=True)
        assert 'Impressão em Lote de QR Codes' in html
        print('[OK] Página de impressão de QR codes carregada')

def test_exportar_relatorio_csv():
    """Testa exportação CSV de relatório diário."""
    # Usar uma data que existe no banco (hoje)
    from datetime import date
    data_hoje = date.today().isoformat()
    with app.test_client() as client:
        resp = client.get(f'/relatorios/{data_hoje}/exportar?formato=csv')
        assert resp.status_code == 200, f'Exportação CSV retornou {resp.status_code}'
        assert 'text/csv' in resp.content_type
        print('[OK] Exportação CSV funciona')

def test_exportar_relatorio_pdf():
    """Testa exportação PDF de relatório diário."""
    from datetime import date
    data_hoje = date.today().isoformat()
    with app.test_client() as client:
        resp = client.get(f'/relatorios/{data_hoje}/exportar?formato=pdf')
        # Pode retornar 200 ou 302 (redirect se não houver dados)
        if resp.status_code == 200:
            assert 'application/pdf' in resp.content_type
            print('[OK] Exportação PDF funciona (dados existem)')
        elif resp.status_code == 302:
            # Redireciona para a página do relatório com flash message
            print('[OK] Exportação PDF redireciona (sem dados)')
        else:
            raise AssertionError(f'Status inesperado: {resp.status_code}')

def test_configuracoes():
    """Testa a tela de configurações."""
    with app.test_client() as client:
        resp = client.get('/configuracoes')
        # A rota /configuracoes redireciona para /admin/configuracoes
        assert resp.status_code == 302, f'Redirecionamento não ocorreu: {resp.status_code}'
        # Seguir o redirecionamento
        resp = client.get('/admin/configuracoes')
        assert resp.status_code == 200, f'Configurações retornou {resp.status_code}'
        html = resp.get_data(as_text=True)
        assert 'Configurações do Sistema' in html
        print('[OK] Tela de configurações carregada')

def test_exportar_configuracoes():
    """Testa exportação de configurações em JSON."""
    with app.test_client() as client:
        resp = client.get('/configuracoes/exportar')
        assert resp.status_code == 200, f'Exportação de configurações retornou {resp.status_code}'
        assert 'application/json' in resp.content_type
        data = resp.get_json()
        assert 'escola' in data
        assert 'whatsapp' in data
        assert 'sistema' in data
        assert 'callmebot_apikey' not in data.get('whatsapp', {})
        print('[OK] Exportação de configurações funciona')

def test_backup():
    """Testa o download do backup do banco de dados."""
    with app.test_client() as client:
        resp = client.get('/backup')
        if resp.status_code == 200:
            assert 'application/vnd.sqlite3' in resp.content_type
            print('[OK] Download do backup funciona')
        elif resp.status_code == 302:
            # Banco de dados não encontrado, redireciona para dashboard
            print('[OK] Backup redireciona (banco não encontrado)')
        else:
            raise AssertionError(f'Status inesperado: {resp.status_code}')

def test_liberacao_forcada():
    """Testa liberação forçada na cantina e presença no relatório diário."""
    from datetime import date, datetime
    from pathlib import Path
    from config import QRCODE_DIR
    from database import get_db
    from models import cadastrar_aluno, relatorio_detalhado_data
    from settings import TURMAS, TURNOS

    matricula = f"FORCE{datetime.now().strftime('%H%M%S%f')}"
    aluno = cadastrar_aluno('Aluno Liberacao Forcada Teste', matricula, TURMAS[0], TURNOS[0])

    try:
        with app.test_client() as client:
            resp = client.post('/api/cantina/liberacao-forcada', json={
                'qrcode_hash': aluno['qrcode_hash'],
                'motivo': 'Teste automatizado',
                'responsavel': 'test_prompt6_routes',
            })
            assert resp.status_code == 200, f'Liberação forçada retornou {resp.status_code}'
            data = resp.get_json()
            assert data['status'] == 'liberado_forcado'

        relatorio = relatorio_detalhado_data(date.today().isoformat())
        assert any(item['matricula'] == matricula for item in relatorio['tabelas']['liberacoes_forcadas'])
        print('[OK] Liberação forçada registrada e incluída no relatório')
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM alunos WHERE matricula = ?', (matricula,))
        row = cur.fetchone()
        if row:
            aluno_id = row['id']
            cur.execute('DELETE FROM liberacoes_forcadas WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM checkin_cantina WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM checkin_portaria WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
            conn.commit()
        conn.close()
        qr_path = Path(QRCODE_DIR) / f'{matricula}.png'
        if qr_path.exists():
            qr_path.unlink()

def test_importar_alunos_csv():
    """Testa importação administrativa de alunos por CSV."""
    from datetime import datetime
    from pathlib import Path
    from config import QRCODE_DIR
    from database import get_db
    from settings import TURMAS, TURNOS

    matricula = f"IMPORT{datetime.now().strftime('%H%M%S%f')}"
    csv_data = f"nome,matricula,turma,turno\nAluno Importado Teste,{matricula},{TURMAS[0]},{TURNOS[0]}\n"

    try:
        with app.test_client() as client:
            resp = client.post('/alunos/importar', data={
                'arquivo_csv': (io.BytesIO(csv_data.encode('utf-8')), 'alunos.csv')
            }, content_type='multipart/form-data')
            assert resp.status_code == 200, f'Importação CSV retornou {resp.status_code}'

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM alunos WHERE matricula = ?', (matricula,))
        row = cur.fetchone()
        conn.close()
        assert row is not None
        print('[OK] Importação CSV pela interface funciona')
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM alunos WHERE matricula = ?', (matricula,))
        row = cur.fetchone()
        if row:
            aluno_id = row['id']
            cur.execute('DELETE FROM liberacoes_forcadas WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM checkin_cantina WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM checkin_portaria WHERE aluno_id = ?', (aluno_id,))
            cur.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
            conn.commit()
        conn.close()
        qr_path = Path(QRCODE_DIR) / f'{matricula}.png'
        if qr_path.exists():
            qr_path.unlink()

def test_seed_script():
    """Testa se o script seed.py pode ser importado e executa sem erros."""
    import seed
    # Verifica se as funções principais estão definidas
    assert hasattr(seed, 'criar_alunos')
    assert hasattr(seed, 'simular_checkins')
    assert hasattr(seed, 'simular_relatorios_enviados')
    print('[OK] Script seed.py importado corretamente')

def test_run_script():
    """Testa se o script run.py pode ser importado."""
    import run
    # Verifica se a função principal está definida
    assert hasattr(run, 'main')
    print('[OK] Script run.py importado corretamente')

if __name__ == '__main__':
    try:
        print('=' * 60)
        print('TESTES DAS FUNCIONALIDADES DO PROMPT 6')
        print('=' * 60)
        test_imprimir_qrcodes()
        test_exportar_relatorio_csv()
        test_exportar_relatorio_pdf()
        test_configuracoes()
        test_exportar_configuracoes()
        test_backup()
        test_liberacao_forcada()
        test_importar_alunos_csv()
        test_seed_script()
        test_run_script()
        print('\n[SUCESSO] Todos os testes passaram.')
    except Exception as e:
        print(f'\n[FALHA] Teste falhou: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
