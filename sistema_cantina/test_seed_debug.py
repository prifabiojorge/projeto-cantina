#!/usr/bin/env python3
"""
Debug script to test seed simulation.
"""
import sys
import os
import random
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, get_db
from models import (
    cadastrar_aluno, listar_alunos, buscar_aluno_por_matricula,
    registrar_checkin_portaria, registrar_checkin_cantina
)
from config import TURMAS, TURNOS, QRCODE_DIR

def criar_alunos(qtd):
    """Cria alunos de teste."""
    alunos = []
    for i in range(qtd):
        nome = f"Aluno Teste {i+1}"
        matricula = f"TEST{i+1:03d}"
        turma = random.choice(TURMAS)
        turno = random.choice(TURNOS)
        ativo = True
        try:
            aluno = cadastrar_aluno(nome, matricula, turma, turno, ativo)
            alunos.append(aluno)
            print(f"  Criado {nome}")
        except Exception as e:
            print(f"  Erro ao criar aluno {nome}: {e}")
    return alunos

def simular_checkins_debug(dias=5):
    """Simula check-ins com debug."""
    print(f"Simulando check-ins dos últimos {dias} dias...")
    
    alunos = listar_alunos(ativo=True)
    print(f"Total alunos ativos: {len(alunos)}")
    
    hoje = date.today()
    checkins_portaria = 0
    checkins_cantina = 0
    
    for i in range(dias):
        data_simulada = hoje - timedelta(days=i)
        print(f"\n  Dia {i}: {data_simulada.isoformat()}")
        
        porcentagem_portaria = random.uniform(0.7, 0.9)
        qtd_portaria = int(len(alunos) * porcentagem_portaria)
        alunos_portaria = random.sample(alunos, qtd_portaria)
        print(f"    Alunos portaria: {qtd_portaria}")
        
        for aluno in alunos_portaria:
            try:
                # Registrar check-in portaria
                result = registrar_checkin_portaria(aluno['qrcode_hash'], data_iso=data_simulada.isoformat())
                if result['status'] == 'ok':
                    checkins_portaria += 1
                else:
                    print(f"    Status portaria: {result['status']}")
                
                # 80% dos que passam pela portaria almoçam
                if random.random() < 0.8:
                    result2 = registrar_checkin_cantina(aluno['qrcode_hash'], data_iso=data_simulada.isoformat())
                    if result2['status'] == 'ok':
                        checkins_cantina += 1
                    else:
                        print(f"    Status cantina: {result2['status']}")
            except Exception as e:
                print(f"    Exceção: {e}")
    
    print(f"\n[OK] {checkins_portaria} check-ins na portaria simulados.")
    print(f"[OK] {checkins_cantina} check-ins na cantina simulados.")

def main():
    print("=== DEBUG SEED ===")
    init_db()
    
    # Criar 5 alunos
    alunos = criar_alunos(5)
    
    # Simular 5 dias
    simular_checkins_debug(5)
    
    # Verificar banco
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT data, COUNT(*) FROM checkin_portaria GROUP BY data ORDER BY data')
    print("\nCheck-ins por data (portaria):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    cursor.execute('SELECT data, COUNT(*) FROM checkin_cantina GROUP BY data ORDER BY data')
    print("Check-ins por data (cantina):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    conn.close()

if __name__ == '__main__':
    main()