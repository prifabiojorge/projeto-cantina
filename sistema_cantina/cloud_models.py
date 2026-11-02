"""Persistencia Supabase para as interfaces usadas pelas rotas legadas."""
import os
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from supabase import create_client
from postgrest.exceptions import APIError

LOCAL_TZ = timezone(timedelta(hours=-3))


def agora():
    return datetime.now(LOCAL_TZ)


def hoje():
    return agora().date().isoformat()


@lru_cache(maxsize=1)
def client():
    return create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])


def rows(table, inicio=None, fim=None, **filters):
    result = []
    while True:
        query = client().table(table).select('*').order('id')
        if inicio:
            query = query.gte('data', inicio)
        if fim:
            query = query.lte('data', fim)
        for key, value in filters.items():
            query = query.eq(key, value)
        page = query.range(len(result), len(result) + 499).execute().data or []
        result.extend(page)
        if len(page) < 500:
            return result


def buscar_aluno_por_id(id):
    # Invalid route identifiers must produce a normal not-found response.
    try:
        uuid.UUID(str(id))
    except ValueError:
        return None
    return next(iter(rows('alunos', id=id)), None)


def buscar_aluno_por_matricula(matricula):
    return next(iter(rows('alunos', matricula=matricula)), None)


def buscar_aluno_por_qrcode(qrcode_hash):
    return next(iter(rows('alunos', qrcode_hash=qrcode_hash, ativo=True)), None)


def listar_alunos(filtro_turma=None, filtro_turno=None, ativo=None):
    filtros = {}
    if filtro_turma:
        filtros['turma'] = filtro_turma
    if ativo is not None:
        filtros['ativo'] = ativo
    return sorted(rows('alunos', **filtros), key=lambda a: (a['turma'], a['nome']))


def validar_aluno(nome, turma):
    from settings import TURMAS
    if not nome.strip() or turma not in TURMAS:
        raise ValueError('Nome ou turma invalida.')


def cadastrar_aluno(nome, matricula, turma, turno='Integral'):
    validar_aluno(nome, turma)
    if not matricula.strip():
        raise ValueError('Matricula obrigatoria.')
    payload = dict(nome=nome.strip(), matricula=matricula.strip(), turma=turma,
                   turno='Integral', qrcode_hash=str(uuid.uuid4()), ativo=True)
    try:
        return client().table('alunos').insert(payload).execute().data[0]
    except APIError as exc:
        if exc.code == '23505':
            raise ValueError('Matricula ja cadastrada.') from exc
        raise


def editar_aluno(id, nome, turma, turno='Integral'):
    validar_aluno(nome, turma)
    client().table('alunos').update(dict(nome=nome.strip(), turma=turma, turno='Integral')).eq('id', id).execute()


def desativar_aluno(id):
    client().table('alunos').update({'ativo': False}).eq('id', id).execute()


def reativar_aluno(id):
    client().table('alunos').update({'ativo': True}).eq('id', id).execute()


def estado(qrcode_hash, data, cantina=False):
    aluno = next(iter(rows('alunos', qrcode_hash=qrcode_hash)), None)
    if not aluno:
        return {'status': 'nao_encontrado', 'aluno': None}
    status = 'liberado'
    if not aluno['ativo']:
        status = 'inativo'
    elif cantina and rows('checkin_cantina', aluno_id=aluno['id'], data=data):
        status = 'ja_almocou'
    elif cantina and not rows('checkin_portaria', aluno_id=aluno['id'], data=data):
        status = 'sem_checkin_portaria'
    return {'status': status, 'aluno': aluno}


def verificar_estado_aluno_para_almoco(qrcode_hash):
    return estado(qrcode_hash, hoje(), cantina=True)


def registrar(qrcode_hash, data_iso, hora, cantina):
    data = data_iso or hoje()
    datetime.fromisoformat(data)
    result = estado(qrcode_hash, data, cantina)
    if result['status'] != 'liberado':
        return result
    table, campo = ('checkin_cantina', 'hora_almoco') if cantina else ('checkin_portaria', 'hora_checkin')
    timestamp = datetime.fromisoformat(f'{data}T{hora}').replace(tzinfo=LOCAL_TZ).isoformat() if hora else agora().isoformat()
    try:
        client().table(table).insert(dict(aluno_id=result['aluno']['id'], data=data, **{campo: timestamp})).execute()
        result['status'] = 'ok'
    except APIError as exc:
        if exc.code != '23505':
            raise
        result['status'] = 'ja_almocou' if cantina else 'ja_registrado'
    return result


def registrar_checkin_portaria(qrcode_hash, data_iso=None, hora_checkin=None):
    return registrar(qrcode_hash, data_iso, hora_checkin, False)


def registrar_checkin_cantina(qrcode_hash, data_iso=None, hora_almoco=None):
    return registrar(qrcode_hash, data_iso, hora_almoco, True)


def registrar_liberacao_forcada(qrcode_hash, motivo, usuario_responsavel=None, data_iso=None):
    if len((motivo or '').strip()) < 3:
        return {'status': 'motivo_invalido', 'aluno': None}
    return client().rpc('cantina_liberar', dict(p_hash=qrcode_hash, p_motivo=motivo.strip(),
                       p_responsavel=usuario_responsavel or 'cantina', p_data=data_iso or hoje())).execute().data


def contar_checkins_portaria_hoje():
    return client().table('checkin_portaria').select('id', count='exact').eq('data', hoje()).limit(1).execute().count


def contar_checkins_cantina_hoje():
    return client().table('checkin_cantina').select('id', count='exact').eq('data', hoje()).limit(1).execute().count


def estatisticas_almoco_hoje():
    p, c = contar_checkins_portaria_hoje(), contar_checkins_cantina_hoje()
    return dict(total_almocaram=c, total_esperado=p, percentual=round(c / p * 100, 1) if p else 0,
                hora_atual=agora().strftime('%H:%M'), data=hoje())


def grupos(alunos, campo):
    return [{campo: k, 'quantidade': v} for k, v in sorted(Counter(a[campo] for a in alunos).items())]


def relatorio_detalhado_data(data):
    datetime.fromisoformat(data)
    alunos = {a['id']: a for a in rows('alunos')}
    def juntar(table, hora):
        registros = []
        for item in rows(table, data=data):
            aluno = alunos.get(item['aluno_id'])
            if aluno:
                registro = {k: aluno[k] for k in ('id', 'matricula', 'nome', 'turma', 'turno')}
                registro[hora] = item.get(hora, item.get('criado_em'))
                if table == 'liberacoes_forcadas':
                    registro.update(motivo=item['motivo'], usuario_responsavel=item.get('usuario_responsavel'))
                registros.append(registro)
        return sorted(registros, key=lambda r: r[hora])
    p = juntar('checkin_portaria', 'hora_checkin')
    c = juntar('checkin_cantina', 'hora_almoco')
    ids = {a['id'] for a in c}
    d = [a for a in p if a['id'] not in ids]
    l = juntar('liberacoes_forcadas', 'hora_liberacao')
    return dict(data=data, tabelas=dict(checkins_portaria=p, checkins_cantina=c, desistencias=d, liberacoes_forcadas=l),
                totais=dict(portaria=len(p), cantina=len(c), desistencias=len(d), liberacoes_forcadas=len(l)))


def estatisticas_gerais():
    alunos = listar_alunos(ativo=True)
    t = relatorio_detalhado_data(hoje())['totais']
    return dict(total_alunos_ativos=len(alunos), alunos_por_turma=grupos(alunos, 'turma'),
                alunos_por_turno=grupos(alunos, 'turno'), portaria_hoje=t['portaria'], cantina_hoje=t['cantina'],
                esperados_almoco=t['desistencias'], data_hoje=hoje())


def historico_checkins(dias=7):
    dias = max(1, min(int(dias), 366))
    inicio = (agora().date() - timedelta(days=dias-1)).isoformat()
    registros = []
    for table in ('checkin_portaria', 'checkin_cantina'):
        items = []
        offset = 0
        while True:
            page = client().table(table).select('aluno_id,data').gte('data', inicio).lte('data', hoje()).order('id').range(offset, offset+499).execute().data
            items.extend(page)
            if len(page) < 500:
                break
            offset += 500
        registros.append(items)
    p, c = [defaultdict(set), defaultdict(set)]
    for mapa, items in zip((p, c), registros):
        for item in items:
            mapa[item['data']].add(item['aluno_id'])
    result = []
    for i in range(dias):
        data = (agora().date() - timedelta(days=dias-1-i)).isoformat()
        result.append(dict(data=data, portaria=len(p[data]), cantina=len(c[data]), sem_almoco=len(p[data]-c[data]), total_alunos=len(p[data])))
    return result


def historico_almoco_semanal(dias=7):
    h = historico_checkins(dias)
    return dict(datas=[r['data'] for r in h], portaria=[r['portaria'] for r in h], cantina=[r['cantina'] for r in h])


def almocos_por_turma_hoje():
    g = grupos(relatorio_detalhado_data(hoje())['tabelas']['checkins_cantina'], 'turma')
    return dict(turmas=[i['turma'] for i in g], quantidades=[i['quantidade'] for i in g],
                cores=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#8AC926', '#1982C4', '#777777', '#00AA88'][:len(g)])


def ultimas_atividades(limite=10):
    t = relatorio_detalhado_data(hoje())['tabelas']
    atividades = []
    for tipo, tabela, campo in [('portaria', 'checkins_portaria', 'hora_checkin'), ('cantina', 'checkins_cantina', 'hora_almoco')]:
        for a in t[tabela]:
            dt = datetime.fromisoformat(a[campo]).astimezone(LOCAL_TZ)
            atividades.append(dict(tipo=tipo, nome=a['nome'], turma=a['turma'], hora=dt.isoformat(), hora_display=dt.strftime('%H:%M:%S')))
    return sorted(atividades, key=lambda a: a['hora'], reverse=True)[:limite]


def relatorio_detalhado(data_inicio=None, data_fim=None, turma=None, turno=None):
    inicio = data_inicio or (agora().date()-timedelta(days=7)).isoformat()
    fim = data_fim or hoje()
    start, end = datetime.fromisoformat(inicio).date(), datetime.fromisoformat(fim).date()
    if end < start or (end-start).days > 366:
        raise ValueError('Periodo invalido (maximo 366 dias).')
    alunos = {a['id']: a for a in rows('alunos')}
    por_data = [defaultdict(list), defaultdict(list)]
    for mapa, tabela in zip(por_data, ('checkin_portaria', 'checkin_cantina')):
        for item in rows(tabela, inicio=inicio, fim=fim):
            aluno = alunos.get(item['aluno_id'])
            if aluno and (not turma or aluno['turma'] == turma):
                mapa[item['data']].append(aluno)
    detalhes = []
    unicos_p, unicos_c, sem = set(), set(), set()
    for i in range((end-start).days+1):
        data = (start+timedelta(days=i)).isoformat()
        ps, cs = por_data[0][data], por_data[1][data]
        unicos_p.update(a['id'] for a in ps)
        unicos_c.update(a['id'] for a in cs)
        sem.update({a['id'] for a in ps}-{a['id'] for a in cs})
        for tr in sorted({a['turma'] for a in ps+cs}):
            p, c = [a for a in ps if a['turma']==tr], [a for a in cs if a['turma']==tr]
            detalhes.append(dict(data=data, turma=tr, turno='Integral', total_portaria=len(p), total_cantina=len(c), nomes_portaria=[a['nome'] for a in p]))
    return dict(periodo=dict(inicio=inicio, fim=fim), filtros=dict(turma=turma, turno=None), detalhes=list(reversed(detalhes)),
                totais=dict(alunos_unicos_portaria=len(unicos_p), alunos_unicos_cantina=len(unicos_c), alunos_sem_almoco=len(sem)))


def gerar_relatorio_portaria_hoje():
    alunos = relatorio_detalhado_data(hoje())['tabelas']['checkins_portaria']
    g = grupos(alunos, 'turma')
    return dict(total=len(alunos), detalhes_turma=g, detalhes_turno=[],
                texto_detalhes='\n'.join(f"{a['turma']}: {a['quantidade']} alunos" for a in g))


def get_config(chave, default=None):
    item = next(iter(rows('configuracoes', chave=chave)), None)
    return item['valor'] if item else default


def set_config(chave, valor, descricao=None):
    payload = dict(chave=chave, valor=str(valor))
    if descricao is not None:
        payload['descricao'] = descricao
    client().table('configuracoes').upsert(payload, on_conflict='chave').execute()


def get_all_config():
    return sorted(rows('configuracoes'), key=lambda a: a['chave'])


def relatorio_ja_enviado_hoje():
    return bool(rows('relatorios_enviados', data=hoje(), status='enviado'))


def registrar_relatorio_enviado(total_esperado, status='enviado', mensagem=None):
    client().table('relatorios_enviados').upsert(dict(data=hoje(), total_esperado=total_esperado,
        status='falhou' if status == 'falha' else status, mensagem=mensagem,
        enviado_em=agora().isoformat() if status=='enviado' else None), on_conflict='data').execute()
    return True
