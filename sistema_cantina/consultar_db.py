"""
Script para executar consultas SQL no banco de dados.
Uso: python consultar_db.py "SELECT * FROM alunos LIMIT 5"
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / 'cantina.db'


def executar_sql(sql, params=None):
    """Executa uma consulta SQL e retorna os resultados."""
    if not DB_PATH.exists():
        print(f"ERRO: Banco de dados nao encontrado: {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        sql_upper = sql.strip().upper()
        
        if sql_upper.startswith('SELECT') or sql_upper.startswith('PRAGMA'):
            # Consulta de leitura
            rows = cursor.fetchall()
            
            if not rows:
                print("Nenhum resultado encontrado.")
                return
            
            # Tentar obter nomes das colunas
            try:
                colunas = [desc[0] for desc in cursor.description]
                print(" | ".join(colunas))
                print("-" * 50)
            except:
                pass
            
            for row in rows:
                print(" | ".join(str(v) for v in row))
            
            print(f"\nTotal: {len(rows)} registros")
        else:
            # Comando de escrita
            conn.commit()
            print(f"OK: {cursor.rowcount} linhas afetadas")
    
    except sqlite3.Error as e:
        print(f"ERRO SQL: {e}")
    
    finally:
        conn.close()


def modo_interativo():
    """Modo interativo para executar múltiplas consultas."""
    print("=== Consulta SQL ao Banco de Dados ===")
    print("Digite SQL ou 'sair' para encerrar")
    print(f"Banco: {DB_PATH}")
    print()
    
    while True:
        try:
            sql = input("SQL> ").strip()
            
            if sql.lower() in ('sair', 'exit', 'quit', '.quit'):
                print("Encerrando...")
                break
            
            if not sql:
                continue
            
            if sql.lower() == 'tabelas':
                sql = "SELECT name FROM sqlite_master WHERE type='table'"
            elif sql.lower() == 'help' or sql.lower() == 'ajuda':
                print("\nComandos disponiveis:")
                print("  tabelas - Lista todas as tabelas")
                print("  sair    - Encerra o programa")
                print("  help    - Mostra esta ajuda")
                print("\nExemplos SQL:")
                print("  SELECT * FROM alunos LIMIT 5")
                print("  SELECT COUNT(*) FROM checkin_portaria")
                print("  SELECT id, nome, matricula FROM alunos WHERE nome LIKE '%Joao%'")
                print()
                continue
            
            executar_sql(sql)
            print()
        
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except EOFError:
            break


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sql = ' '.join(sys.argv[1:])
        executar_sql(sql)
    else:
        modo_interativo()
