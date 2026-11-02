"""Substitui cadastros e historicos, com copia de seguranca antes da limpeza."""
import json
import re
import sqlite3
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from migrar_sqlite_para_supabase import ROOT, DB_PATH, _client


def ler_lista():
    alunos = []
    turma = None
    for linha in (ROOT / 'Lista Unificada de Alunos - CISEB 2026 v2.md').read_text(encoding='utf-8').splitlines():
        cabecalho = re.search(r'TURMA:\s*(\d{3})', linha)
        if cabecalho:
            turma = cabecalho.group(1)
        aluno = re.fullmatch(r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|', linha)
        if aluno:
            if turma is None:
                raise ValueError('Aluno sem turma')
            numero, nome = aluno.groups()
            alunos.append(dict(nome=nome.strip(), turma=turma, turno='Integral',
                               matricula=f'2026-{turma}-{int(numero):02d}',
                               qrcode_hash=str(uuid.uuid4()), ativo=True))
    assert alunos and len({a['matricula'] for a in alunos}) == len(alunos), 'Lista vazia ou chamada repetida'
    return alunos


def consultar_todos(client, tabela):
    rows = []
    while True:
        pagina = client.table(tabela).select('*').order('id').range(len(rows), len(rows) + 499).execute().data
        rows.extend(pagina)
        if len(pagina) < 500:
            return rows


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--executar', action='store_true')
    args = parser.parse_args()
    alunos = ler_lista()
    print('Lista validada:', len(alunos), 'alunos;', dict(Counter(a['turma'] for a in alunos)))
    if not args.executar:
        return
    client = _client()
    tabelas = ['liberacoes_forcadas', 'checkin_cantina', 'checkin_portaria', 'relatorios_enviados', 'alunos']
    pasta = ROOT / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta.mkdir(parents=True)
    snapshot = {t: consultar_todos(client, t) for t in tabelas}
    (pasta / 'supabase.json').write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
    conn = sqlite3.connect(DB_PATH)
    copia = sqlite3.connect(pasta / 'cantina.db')
    conn.backup(copia)
    copia.close()
    # All remote reads and backups finish before the first destructive operation.
    for tabela in tabelas:
        client.table(tabela).delete().not_.is_('id', 'null').execute()
    client.table('alunos').insert(alunos).execute()
    assert client.table('alunos').select('id', count='exact').limit(1).execute().count == len(alunos)
    with conn:
        for tabela in tabelas:
            conn.execute(f'DELETE FROM {tabela}')
        conn.executemany('INSERT INTO alunos (nome,matricula,turma,turno,qrcode_hash,ativo) VALUES (:nome,:matricula,:turma,:turno,:qrcode_hash,:ativo)', alunos)
        for chave, valor in [('nome_escola', 'Escola Estadual Celso Rodrigues'), ('turmas_disponiveis', '\n'.join(sorted({a['turma'] for a in alunos}))), ('turnos_disponiveis', 'Integral')]:
            conn.execute('INSERT INTO configuracoes (chave,valor) VALUES (?,?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor', (chave, valor))
            client.table('configuracoes').upsert(dict(chave=chave, valor=valor), on_conflict='chave').execute()
    conn.close()
    config = ROOT / 'sistema_cantina' / 'config_escola.json'
    dados = json.loads(config.read_text(encoding='utf-8'))
    dados['escola'].update(nome='Escola Estadual Celso Rodrigues', turmas=sorted({a['turma'] for a in alunos}), turnos=['Integral'])
    config.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Substituicao concluida. Backup privado:', pasta)


if __name__ == '__main__':
    main()
