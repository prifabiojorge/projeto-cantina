#!/usr/bin/env python
"""
Teste das novas funções do dashboard (Prompt 5).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, get_db
from models import (
    dashboard_dados, 
    relatorio_detalhado_data,
    historico_almoco_semanal,
    almocos_por_turma_hoje,
    ultimas_atividades
)
from datetime import date, timedelta

def test_dashboard_dados():
    """Testa a função dashboard_dados()."""
    print("Testando dashboard_dados()...")
    try:
        dados = dashboard_dados()
        assert isinstance(dados, dict)
        assert 'cards' in dados
        assert 'grafico_turmas' in dados
        assert 'historico_semanal' in dados
        assert 'ultimas_atividades' in dados
        assert 'estatisticas_gerais' in dados
        
        cards = dados['cards']
        assert 'progresso_almoco' in cards
        assert 'desperdicio_evitado' in cards
        assert 'checkins_portaria' in cards
        assert 'checkins_cantina' in cards
        
        print("[OK] dashboard_dados() OK")
        return True
    except Exception as e:
        print(f"[ERRO] Erro em dashboard_dados(): {e}")
        return False

def test_relatorio_detalhado_data():
    """Testa relatório por data específica."""
    print("\nTestando relatorio_detalhado_data()...")
    try:
        hoje = date.today().isoformat()
        relatorio = relatorio_detalhado_data(hoje)
        
        assert isinstance(relatorio, dict)
        assert 'data' in relatorio
        assert 'tabelas' in relatorio
        assert 'totais' in relatorio
        
        tabelas = relatorio['tabelas']
        assert 'checkins_portaria' in tabelas
        assert 'checkins_cantina' in tabelas
        assert 'desistencias' in tabelas
        assert 'liberacoes_forcadas' in tabelas
        
        totais = relatorio['totais']
        assert 'portaria' in totais
        assert 'cantina' in totais
        assert 'desistencias' in totais
        assert 'liberacoes_forcadas' in totais
        
        print(f"[OK] relatorio_detalhado_data('{hoje}') OK")
        return True
    except Exception as e:
        print(f"[ERRO] Erro em relatorio_detalhado_data(): {e}")
        return False

def test_historico_almoco_semanal():
    """Testa histórico semanal."""
    print("\nTestando historico_almoco_semanal()...")
    try:
        historico = historico_almoco_semanal(dias=7)
        
        assert isinstance(historico, dict)
        assert 'datas' in historico
        assert 'portaria' in historico
        assert 'cantina' in historico
        
        assert len(historico['datas']) == 7
        assert len(historico['portaria']) == 7
        assert len(historico['cantina']) == 7
        
        print("[OK] historico_almoco_semanal() OK")
        return True
    except Exception as e:
        print(f"[ERRO] Erro em historico_almoco_semanal(): {e}")
        return False

def test_almocos_por_turma_hoje():
    """Testa almoços por turma hoje."""
    print("\nTestando almocos_por_turma_hoje()...")
    try:
        dados = almocos_por_turma_hoje()
        
        assert isinstance(dados, dict)
        assert 'turmas' in dados
        assert 'quantidades' in dados
        assert 'cores' in dados
        
        assert len(dados['turmas']) == len(dados['quantidades'])
        assert len(dados['cores']) >= len(dados['turmas']) or len(dados['cores']) == 0
        
        print("[OK] almocos_por_turma_hoje() OK")
        return True
    except Exception as e:
        print(f"[ERRO] Erro em almocos_por_turma_hoje(): {e}")
        return False

def test_ultimas_atividades():
    """Testa últimas atividades."""
    print("\nTestando ultimas_atividades()...")
    try:
        atividades = ultimas_atividades(limite=5)
        
        assert isinstance(atividades, list)
        assert len(atividades) <= 5
        
        for atividade in atividades:
            assert 'tipo' in atividade
            assert atividade['tipo'] in ('portaria', 'cantina')
            assert 'nome' in atividade
            assert 'turma' in atividade
            assert 'hora' in atividade
            assert 'hora_display' in atividade
        
        print("[OK] ultimas_atividades() OK")
        return True
    except Exception as e:
        print(f"[ERRO] Erro em ultimas_atividades(): {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTES DAS FUNÇÕES DO DASHBOARD (PROMPT 5)")
    print("=" * 60)
    
    # Inicializar banco de dados
    init_db()
    
    testes = [
        test_dashboard_dados,
        test_relatorio_detalhado_data,
        test_historico_almoco_semanal,
        test_almocos_por_turma_hoje,
        test_ultimas_atividades
    ]
    
    resultados = []
    for teste in testes:
        resultados.append(teste())
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print("=" * 60)
    
    sucessos = sum(resultados)
    total = len(resultados)
    
    if sucessos == total:
        print(f"[OK] TODOS OS {total} TESTES PASSARAM!")
        return 0
    else:
        print(f"[AVISO]  {sucessos}/{total} testes passaram.")
        return 1

if __name__ == '__main__':
    sys.exit(main())