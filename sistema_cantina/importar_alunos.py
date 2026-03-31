"""
Script para importação em massa de alunos via CSV.
Uso: python importar_alunos.py alunos_reais.csv

Formato do CSV:
  nome,matricula,turma,turno
  João da Silva,20250001,1ºA,Manhã
"""

import sys
import csv
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from models import cadastrar_aluno
from settings import TURMAS, TURNOS


def importar_alunos(arquivo_csv):
    """
    Lê um arquivo CSV e cadastra os alunos no sistema.
    
    Args:
        arquivo_csv (str): Caminho para o arquivo CSV
        
    Returns:
        tuple: (sucessos, falhas, erros)
    """
    if not Path(arquivo_csv).exists():
        print(f"Arquivo nao encontrado: {arquivo_csv}")
        return 0, 0, []
    
    sucessos = 0
    falhas = 0
    erros = []
    
    print(f"Lendo arquivo: {arquivo_csv}")
    print(f"Turmas validas: {', '.join(TURMAS)}")
    print(f"Turnos validos: {', '.join(TURNOS)}")
    print("=" * 60)
    
    with open(arquivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Verificar cabeçalho
        fieldnames = reader.fieldnames or []
        if 'nome' not in fieldnames or 'matricula' not in fieldnames:
            print("ERRO: CSV deve ter colunas 'nome' e 'matricula'")
            return 0, 0, ["Cabecalho invalido"]
        
        for i, row in enumerate(reader, start=2):  # linha 2 em diante (1 é cabeçalho)
            nome = row.get('nome', '').strip()
            matricula = row.get('matricula', '').strip()
            turma = row.get('turma', '').strip()
            turno = row.get('turno', '').strip()
            
            # Validações básicas
            if not nome:
                msg = f"Linha {i}: Nome vazio"
                print(f"AVISO: {msg}")
                erros.append(msg)
                falhas += 1
                continue
            
            if not matricula:
                msg = f"Linha {i}: Matricula vazia para {nome}"
                print(f"AVISO: {msg}")
                erros.append(msg)
                falhas += 1
                continue
            
            if turma and turma not in TURMAS:
                msg = f"Linha {i}: Turma '{turma}' invalida para {nome}"
                print(f"AVISO: {msg}")
                erros.append(msg)
                falhas += 1
                continue
            
            if turno and turno not in TURNOS:
                msg = f"Linha {i}: Turno '{turno}' invalido para {nome}"
                print(f"AVISO: {msg}")
                erros.append(msg)
                falhas += 1
                continue
            
            # Valores padrão se não informados
            if not turma:
                turma = TURMAS[0] if TURMAS else '1ºA'
            if not turno:
                turno = TURNOS[0] if TURNOS else 'Manhã'
            
            try:
                aluno = cadastrar_aluno(nome, matricula, turma, turno)
                print(f"OK: {nome} ({matricula}) - {turma} - {turno}")
                sucessos += 1
            except ValueError as e:
                msg = f"Linha {i}: {nome} - {e}"
                print(f"ERRO: {msg}")
                erros.append(msg)
                falhas += 1
            except Exception as e:
                msg = f"Linha {i}: {nome} - Erro: {e}"
                print(f"ERRO: {msg}")
                erros.append(msg)
                falhas += 1
    
    print("=" * 60)
    print(f"RESUMO:")
    print(f"   Importados com sucesso: {sucessos}")
    print(f"   Falhas: {falhas}")
    print(f"   Total processado: {sucessos + falhas}")
    
    if erros:
        print(f"\nDetalhes dos erros:")
        for erro in erros:
            print(f"   - {erro}")
    
    return sucessos, falhas, erros


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python importar_alunos.py <arquivo.csv>")
        print("Exemplo: python importar_alunos.py alunos_reais.csv")
        print("\nFormato do CSV:")
        print("  nome,matricula,turma,turno")
        print("  João da Silva,20250001,1ºA,Manhã")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    importar_alunos(arquivo)
