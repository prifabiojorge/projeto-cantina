#!/usr/bin/env python3
"""
Script de seed (população) para o Sistema Cantina Escolar.

Gera:
- 60 alunos brasileiros realistas com QR codes
- Check-ins simulados na portaria (últimos 30 dias)
- Check-ins simulados na cantina (últimos 30 dias)
- Relatórios enviados (últimos 7 dias)

Execute com: python seed.py
"""

import sys
import os
import random
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

# Adicionar o diretório atual ao path para importar módulos locais
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, get_db
from models import (
    cadastrar_aluno, listar_alunos, buscar_aluno_por_matricula,
    registrar_checkin_portaria, registrar_checkin_cantina
)
from config import TURMAS, TURNOS, QRCODE_DIR

# Listas de nomes brasileiros realistas
NOMES_MASCULINOS = [
    'João Silva', 'Pedro Santos', 'Lucas Oliveira', 'Gabriel Costa', 'Matheus Pereira',
    'Rafael Souza', 'Felipe Rodrigues', 'Daniel Almeida', 'Gustavo Lima', 'Bruno Carvalho',
    'Enzo Fernandes', 'Arthur Martins', 'Davi Ferreira', 'Bernardo Gomes', 'Heitor Barbosa',
    'Samuel Ribeiro', 'Cauã Castro', 'Vicente Cardoso', 'Eduardo Correia', 'Leonardo Dias',
    'Guilherme Teixeira', 'Nicolas Monteiro', 'Lorenzo Nascimento', 'Henrique Moreira',
    'Benjamin Mendes', 'Joaquim Araújo', 'Vitor Marques', 'Murilo Rocha', 'Ryan Freitas',
    'Breno Cunha'
]

NOMES_FEMININOS = [
    'Maria Silva', 'Ana Santos', 'Julia Oliveira', 'Beatriz Costa', 'Mariana Pereira',
    'Gabriela Souza', 'Isabela Rodrigues', 'Larissa Almeida', 'Letícia Lima', 'Amanda Carvalho',
    'Sophia Fernandes', 'Manuela Martins', 'Laura Ferreira', 'Valentina Gomes', 'Helena Barbosa',
    'Isadora Ribeiro', 'Luana Castro', 'Yasmin Cardoso', 'Clara Correia', 'Cecília Dias',
    'Emanuelly Teixeira', 'Rebeca Monteiro', 'Lívia Nascimento', 'Eloá Moreira',
    'Antonella Mendes', 'Maitê Araújo', 'Lavínia Marques', 'Esther Rocha', 'Sarah Freitas',
    'Elisa Cunha'
]

# Turmas são importadas de config.py (TURMAS)

def gerar_matricula(ano_base=2025):
    """Gera uma matrícula no formato AAMMDDNNN"""
    ano = str(ano_base)[-2:]
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    sequencial = random.randint(1, 999)
    return f"{ano}{mes:02d}{dia:02d}{sequencial:03d}"

def criar_alunos(qtd=60):
    """Cria alunos com dados realistas."""
    print(f"Criando {qtd} alunos...")
    
    alunos_criados = 0
    for i in range(qtd):
        # Escolher gênero aleatoriamente
        if random.random() < 0.5:
            nome = random.choice(NOMES_MASCULINOS)
        else:
            nome = random.choice(NOMES_FEMININOS)
        
        matricula = gerar_matricula()
        turma = random.choice(TURMAS)
        turno = random.choice(TURNOS)
        
        try:
            resultado = cadastrar_aluno(nome, matricula, turma, turno)
            if resultado:
                alunos_criados += 1
                if alunos_criados % 10 == 0:
                    print(f"  {alunos_criados} alunos criados...")
        except Exception as e:
            # Matrícula duplicada ou outro erro
            continue
    
    print(f"[OK] {alunos_criados} alunos criados com sucesso.")
    return alunos_criados

def simular_checkins(dias=30):
    """Simula check-ins na portaria e cantina nos últimos `dias` dias."""
    print(f"Simulando check-ins dos últimos {dias} dias...")
    
    alunos = listar_alunos(ativo=True)
    if not alunos:
        print("[WARN]  Nenhum aluno ativo encontrado.")
        return
    
    hoje = date.today()
    checkins_portaria = 0
    checkins_cantina = 0
    
    for i in range(dias):
        data_simulada = hoje - timedelta(days=i)
        
        # A cada dia, 70-90% dos alunos fazem check-in na portaria
        porcentagem_portaria = random.uniform(0.7, 0.9)
        qtd_portaria = int(len(alunos) * porcentagem_portaria)
        alunos_portaria = random.sample(alunos, qtd_portaria)
        
        for aluno in alunos_portaria:
            try:
                # Registrar check-in portaria
                registrar_checkin_portaria(aluno['qrcode_hash'], data_iso=data_simulada.isoformat())
                checkins_portaria += 1
                
                # 80% dos que passam pela portaria almoçam
                if random.random() < 0.8:
                    # Tempo entre check-in portaria e cantina (5-45 minutos)
                    registrar_checkin_cantina(aluno['qrcode_hash'], data_iso=data_simulada.isoformat())
                    checkins_cantina += 1
            except Exception as e:
                # Check-in duplicado para o mesmo dia, ignorar
                pass
        
        if i % 7 == 0:
            print(f"  Simulados {i+1} dias...")
    
    print(f"[OK] {checkins_portaria} check-ins na portaria simulados.")
    print(f"[OK] {checkins_cantina} check-ins na cantina simulados.")

def simular_relatorios_enviados(dias=7):
    """Simula relatórios enviados nos últimos `dias` dias."""
    print(f"Simulando relatórios enviados dos últimos {dias} dias...")
    
    import sqlite3
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today()
    relatorios = 0
    
    for i in range(dias):
        data_simulada = (hoje - timedelta(days=i)).isoformat()
        # Total esperado aleatório entre 50 e 150
        total_esperado = random.randint(50, 150)
        enviado_em = datetime.now().isoformat(' ', 'seconds')
        
        try:
            cursor.execute('''
                INSERT INTO relatorios_enviados (data, total_esperado, enviado_em)
                VALUES (?, ?, ?)
            ''', (data_simulada, total_esperado, enviado_em))
            relatorios += 1
        except sqlite3.IntegrityError:
            # Relatório já registrado para esta data
            conn.rollback()
        except Exception as e:
            conn.rollback()
    
    conn.commit()
    conn.close()
    print(f"[OK] {relatorios} relatórios simulados.")

def limpar_dados():
    """Remove todos os dados do banco (uso em desenvolvimento)."""
    print("[WARN]  Limpando todos os dados do banco...")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Desativar foreign keys temporariamente
    cursor.execute('PRAGMA foreign_keys = OFF')
    
    cursor.execute('DELETE FROM checkin_portaria')
    cursor.execute('DELETE FROM checkin_cantina')
    cursor.execute('DELETE FROM relatorios_enviados')
    cursor.execute('DELETE FROM alunos')
    cursor.execute('DELETE FROM configuracoes')
    
    # Reinserir configurações padrão
    configuracoes_padrao = [
        ('escola_nome', 'Escola Municipal', 'Nome da escola'),
        ('whatsapp_enabled', 'false', 'Habilitar envio automático de relatório via WhatsApp'),
        ('whatsapp_phone', '', 'Número de telefone para envio do relatório (ex: +5511999999999)'),
        ('whatsapp_send_hour', '8', 'Hora do envio automático (0-23)'),
        ('whatsapp_send_minute', '0', 'Minuto do envio automático (0-59)'),
        ('alarme_som', 'true', 'Habilitar som de alarme na cantina'),
        ('alarme_visual', 'true', 'Habilitar alerta visual na cantina'),
        ('dias_historico', '7', 'Número de dias exibidos no histórico do dashboard')
    ]
    cursor.executemany(
        'INSERT INTO configuracoes (chave, valor, descricao) VALUES (?, ?, ?)',
        configuracoes_padrao
    )
    
    cursor.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()
    
    print("[OK] Dados limpos e configurações padrão restauradas.")

def verificar_qrcodes():
    """Verifica se os QR codes foram gerados corretamente."""
    print("Verificando QR codes...")
    
    alunos = listar_alunos(ativo=True)
    qrcodes_gerados = 0
    qrcodes_faltando = []
    
    for aluno in alunos:
        qrcode_path = QRCODE_DIR / f"{aluno['matricula']}.png"
        if qrcode_path.exists():
            qrcodes_gerados += 1
        else:
            qrcodes_faltando.append(aluno['matricula'])
    
    if qrcodes_faltando:
        print(f"[WARN]  {len(qrcodes_faltando)} QR codes não gerados:")
        for matricula in qrcodes_faltando[:5]:  # Mostrar apenas os 5 primeiros
            print(f"    - {matricula}")
        if len(qrcodes_faltando) > 5:
            print(f"    ... e mais {len(qrcodes_faltando) - 5}")
    else:
        print(f"[OK] Todos os {qrcodes_gerados} QR codes foram gerados.")

def main():
    """Função principal."""
    print("=" * 60)
    print("SEED DO SISTEMA CANTINA ESCOLAR")
    print("=" * 60)
    
    # Inicializar banco de dados
    print("\n1. Inicializando banco de dados...")
    init_db()
    print("[OK] Banco de dados inicializado.")
    
    # Verificar se estamos em modo não interativo (via argumento ou stdin não sendo tty)
    non_interactive = '--non-interactive' in sys.argv or not sys.stdin.isatty()
    
    # Perguntar se deseja limpar dados existentes (com fallback para não interativo)
    if non_interactive:
        print("[WARN]  Modo não interativo, mantendo dados existentes. Alunos duplicados serão ignorados.")
    else:
        try:
            resposta = input("\n[WARN]  Deseja limpar todos os dados existentes? (s/N): ").strip().lower()
            if resposta == 's':
                limpar_dados()
            else:
                print("[WARN]  Mantendo dados existentes. Alunos duplicados serão ignorados.")
        except EOFError:
            print("[WARN]  Modo não interativo, mantendo dados existentes. Alunos duplicados serão ignorados.")
    
    # Criar alunos
    print("\n2. Criando alunos...")
    alunos_criados = criar_alunos(60)
    
    # Simular check-ins
    print("\n3. Simulando check-ins...")
    simular_checkins(30)
    
    # Simular relatórios
    print("\n4. Simulando relatórios enviados...")
    simular_relatorios_enviados(7)
    
    # Verificar QR codes
    print("\n5. Verificando QR codes...")
    verificar_qrcodes()
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("RESUMO DA SEED:")
    print("=" * 60)
    
    alunos = listar_alunos()
    print(f"* Total de alunos: {len(alunos)}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM checkin_portaria')
    portaria = cursor.fetchone()[0]
    print(f"* Check-ins na portaria: {portaria}")
    
    cursor.execute('SELECT COUNT(*) FROM checkin_cantina')
    cantina = cursor.fetchone()[0]
    print(f"* Check-ins na cantina: {cantina}")
    
    cursor.execute('SELECT COUNT(*) FROM relatorios_enviados')
    relatorios = cursor.fetchone()[0]
    print(f"* Relatórios enviados: {relatorios}")
    
    conn.close()
    
    print("\n[OK] Seed concluído com sucesso!")
    print("\n[LIST] Próximos passos:")
    print("   1. Execute o sistema: python run.py")
    print("   2. Acesse http://localhost:5000")
    print("   3. Use as credenciais padrão (se houver)")

if __name__ == '__main__':
    main()