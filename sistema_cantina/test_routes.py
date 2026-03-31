#!/usr/bin/env python3
"""
Teste rápido das rotas do dashboard.
"""
import sys
sys.path.insert(0, '.')

from app import app

print("Rotas registradas:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule}")

# Verificar se as rotas do dashboard existem
endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
required = {'dashboard', 'relatorio_detalhado_view', 'api_historico'}
missing = required - endpoints
if missing:
    print(f"\nERRO: Endpoints faltando: {missing}")
    sys.exit(1)
else:
    print("\n[OK] Todos endpoints do dashboard estão presentes.")

print("\nTeste de importação dos modelos...")
from models import estatisticas_gerais, historico_checkins, relatorio_detalhado
print("[OK] Funções importadas com sucesso.")

# Testar execução (sem erros de sintaxe)
try:
    stats = estatisticas_gerais()
    print(f"[OK] estatisticas_gerais() retornou: {list(stats.keys())}")
except Exception as e:
    print(f"[ERRO] estatisticas_gerais() falhou: {e}")

try:
    historico = historico_checkins(2)
    print(f"[OK] historico_checkins(2) retornou {len(historico)} dias")
except Exception as e:
    print(f"[ERRO] historico_checkins() falhou: {e}")

try:
    relatorio = relatorio_detalhado()
    print(f"[OK] relatorio_detalhado() retornou: {list(relatorio.keys())}")
except Exception as e:
    print(f"[ERRO] relatorio_detalhado() falhou: {e}")

print("\n[OK] Teste concluído.")