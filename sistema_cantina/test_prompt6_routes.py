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
        test_backup()
        test_seed_script()
        test_run_script()
        print('\n[SUCESSO] Todos os testes passaram.')
    except Exception as e:
        print(f'\n[FALHA] Teste falhou: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)