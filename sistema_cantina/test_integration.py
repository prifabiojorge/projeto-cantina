#!/usr/bin/env python3
"""
Teste de integração das rotas do dashboard.
Usa o test client do Flask, não precisa levantar servidor.
"""
import sys
sys.path.insert(0, '.')

from app import app

def test_dashboard():
    with app.test_client() as client:
        resp = client.get('/dashboard')
        assert resp.status_code == 200, f'Dashboard retornou {resp.status_code}'
        print('[OK] Dashboard carregado (HTTP 200)')
        
        # Verifica se o template contém elementos esperados
        html = resp.get_data(as_text=True)
        assert 'Dashboard Administrativo' in html
        assert 'Card' in html  # Pelo menos um card
        print('[OK] Conteúdo HTML parece válido')

def test_relatorio():
    with app.test_client() as client:
        resp = client.get('/relatorio')
        assert resp.status_code == 200, f'Relatório retornou {resp.status_code}'
        print('[OK] Relatório carregado (HTTP 200)')
        
        html = resp.get_data(as_text=True)
        assert 'Relatório Detalhado' in html
        assert 'Filtros' in html
        print('[OK] Conteúdo HTML parece válido')

def test_api_historico():
    with app.test_client() as client:
        resp = client.get('/api/historico')
        assert resp.status_code == 200, f'API histórico retornou {resp.status_code}'
        assert resp.is_json
        data = resp.get_json()
        # Espera-se uma lista
        assert isinstance(data, list)
        print(f'[OK] API histórico retornou {len(data)} dias')

if __name__ == '__main__':
    try:
        test_dashboard()
        test_relatorio()
        test_api_historico()
        print('\n[SUCESSO] Todos os testes de integração passaram.')
    except Exception as e:
        print(f'\n[FALHA] Teste falhou: {e}')
        sys.exit(1)