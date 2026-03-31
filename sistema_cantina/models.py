import qrcode
import sqlite3
import uuid
import logging
from pathlib import Path
from datetime import datetime
from database import get_db
from config import QRCODE_DIR
from settings import TURMAS, TURNOS

logger = logging.getLogger(__name__)

def cadastrar_aluno(nome, matricula, turma, turno):
    if turma not in TURMAS:
        raise ValueError(f'Turma inválida. Opções: {", ".join(TURMAS)}')
    if turno not in TURNOS:
        raise ValueError(f'Turno inválido. Opções: {", ".join(TURNOS)}')
    
    qrcode_hash = str(uuid.uuid4())
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO alunos (nome, matricula, turma, turno, qrcode_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, matricula, turma, turno, qrcode_hash))
        aluno_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        logger.error(f'IntegrityError ao cadastrar aluno {matricula}: {e}')
        if 'UNIQUE' in str(e):
            if 'matricula' in str(e):
                raise ValueError('Matrícula já cadastrada.')
            else:
                raise ValueError('Erro de unicidade no QR code.')
        raise
    except Exception as e:
        conn.rollback()
        logger.exception(f'Erro inesperado ao cadastrar aluno {matricula}: {e}')
        raise
    finally:
        conn.close()
    
    gerar_qrcode_png(qrcode_hash, matricula)
    
    return {
        'id': aluno_id,
        'nome': nome,
        'matricula': matricula,
        'turma': turma,
        'turno': turno,
        'qrcode_hash': qrcode_hash
    }

def gerar_qrcode_png(qrcode_hash, matricula):
    img = qrcode.make(qrcode_hash)
    filename = QRCODE_DIR / f'{matricula}.png'
    with open(filename, 'wb') as f:
        img.save(f)

def listar_alunos(filtro_turma=None, filtro_turno=None, ativo=None):
    """
    Lista alunos com filtros opcionais.
    ativo: True (somente ativos), False (somente inativos), None (todos)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM alunos WHERE 1=1'
    params = []
    
    if ativo is not None:
        query += ' AND ativo = ?'
        params.append(1 if ativo else 0)
    
    if filtro_turma:
        query += ' AND turma = ?'
        params.append(filtro_turma)
    if filtro_turno:
        query += ' AND turno = ?'
        params.append(filtro_turno)
    
    query += ' ORDER BY turma, nome'
    
    cursor.execute(query, params)
    alunos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alunos

def buscar_aluno_por_qrcode(qrcode_hash):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alunos WHERE qrcode_hash = ? AND ativo = 1', (qrcode_hash,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def buscar_aluno_por_matricula(matricula):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alunos WHERE matricula = ?', (matricula,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def editar_aluno(id, nome, turma, turno):
    if turma not in TURMAS:
        raise ValueError(f'Turma inválida. Opções: {", ".join(TURMAS)}')
    if turno not in TURNOS:
        raise ValueError(f'Turno inválido. Opções: {", ".join(TURNOS)}')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE alunos
        SET nome = ?, turma = ?, turno = ?
        WHERE id = ?
    ''', (nome, turma, turno, id))
    conn.commit()
    conn.close()

def desativar_aluno(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE alunos SET ativo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def reativar_aluno(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE alunos SET ativo = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def registrar_checkin_portaria(qrcode_hash, data_iso=None, hora_checkin=None):
    from datetime import datetime, date, timedelta
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca aluno pelo QR code (qualquer status)
    cursor.execute('SELECT * FROM alunos WHERE qrcode_hash = ?', (qrcode_hash,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return {'status': 'nao_encontrado', 'aluno': None}
    
    aluno = dict(row)
    
    # Verifica se aluno está inativo
    if not aluno['ativo']:
        conn.close()
        return {'status': 'inativo', 'aluno': aluno}
    
    # Determina data e hora
    if data_iso is None:
        data_iso = date.today().isoformat()
    if hora_checkin is None:
        # Gera hora razoável conforme turno do aluno
        if aluno['turno'] == 'Manhã':
            hora_checkin = '07:30:00'
        elif aluno['turno'] == 'Tarde':
            hora_checkin = '13:30:00'
        else:
            hora_checkin = '12:00:00'
    
    hora_completa = f'{data_iso} {hora_checkin}'
    
    try:
        cursor.execute('''
            INSERT INTO checkin_portaria (aluno_id, data, hora_checkin)
            VALUES (?, ?, ?)
        ''', (aluno['id'], data_iso, hora_completa))
        conn.commit()
        status = 'ok'
    except sqlite3.IntegrityError:
        # UNIQUE(aluno_id, data) violado → já registrado hoje
        conn.rollback()
        status = 'ja_registrado'
    
    conn.close()
    return {'status': status, 'aluno': aluno}

def contar_checkins_portaria_hoje():
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (hoje,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def registrar_checkin_cantina(qrcode_hash, data_iso=None, hora_almoco=None):
    from datetime import datetime, date
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca aluno pelo QR code (qualquer status)
    cursor.execute('SELECT * FROM alunos WHERE qrcode_hash = ?', (qrcode_hash,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return {'status': 'nao_encontrado', 'aluno': None}
    
    aluno = dict(row)
    
    # Verifica se aluno está inativo
    if not aluno['ativo']:
        conn.close()
        return {'status': 'inativo', 'aluno': aluno}
    
    # Determina data
    if data_iso is None:
        data_iso = date.today().isoformat()
    
    # Verifica se aluno fez check-in na portaria na mesma data
    cursor.execute('SELECT id FROM checkin_portaria WHERE aluno_id = ? AND data = ?', (aluno['id'], data_iso))
    portaria_checkin = cursor.fetchone()
    if portaria_checkin is None:
        conn.close()
        return {'status': 'sem_checkin_portaria', 'aluno': aluno}
    
    # Determina hora do almoço
    if hora_almoco is None:
        if aluno['turno'] == 'Manhã':
            hora_almoco = '12:00:00'
        elif aluno['turno'] == 'Tarde':
            hora_almoco = '13:30:00'
        else:
            hora_almoco = '12:30:00'
    
    hora_completa = f'{data_iso} {hora_almoco}'
    
    try:
        cursor.execute('''
            INSERT INTO checkin_cantina (aluno_id, data, hora_almoco)
            VALUES (?, ?, ?)
        ''', (aluno['id'], data_iso, hora_completa))
        conn.commit()
        status = 'ok'
    except sqlite3.IntegrityError:
        # UNIQUE(aluno_id, data) violado → já almoçou hoje
        conn.rollback()
        # FIX: status mudado de ja_registrado para ja_almocou (alarme depende disso)
        status = 'ja_almocou'
    
    conn.close()
    return {'status': status, 'aluno': aluno}

def contar_checkins_cantina_hoje():
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) FROM checkin_cantina WHERE data = ?', (hoje,))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def estatisticas_almoco_hoje():
    """
    Retorna estatísticas de almoço para a barra inferior da cantina.
    """
    from datetime import date, datetime
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    
    # Total de almoços hoje
    cursor.execute('SELECT COUNT(*) FROM checkin_cantina WHERE data = ?', (hoje,))
    total_almocaram = cursor.fetchone()[0]
    
    # Total de check-ins na portaria hoje (alunos esperados para almoço)
    cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (hoje,))
    total_esperado = cursor.fetchone()[0]
    
    # Percentual
    if total_esperado > 0:
        percentual = round((total_almocaram / total_esperado) * 100, 1)
    else:
        percentual = 0
    
    # Hora atual
    hora_atual = datetime.now().strftime('%H:%M')
    
    conn.close()
    return {
        'total_almocaram': total_almocaram,
        'total_esperado': total_esperado,
        'percentual': percentual,
        'hora_atual': hora_atual,
        'data': hoje
    }

def verificar_estado_aluno_para_almoco(qrcode_hash):
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca aluno pelo QR code
    cursor.execute('SELECT * FROM alunos WHERE qrcode_hash = ?', (qrcode_hash,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return {'status': 'nao_encontrado', 'aluno': None}
    
    aluno = dict(row)
    
    # Verifica se aluno está inativo
    if not aluno['ativo']:
        conn.close()
        return {'status': 'inativo', 'aluno': aluno}
    
    hoje = date.today().isoformat()
    
    # Verifica se aluno fez check-in na portaria hoje
    cursor.execute('SELECT id FROM checkin_portaria WHERE aluno_id = ? AND data = ?', (aluno['id'], hoje))
    portaria_checkin = cursor.fetchone()
    if portaria_checkin is None:
        conn.close()
        return {'status': 'sem_checkin_portaria', 'aluno': aluno}
    
    # Verifica se aluno já fez check-in na cantina hoje
    cursor.execute('SELECT id FROM checkin_cantina WHERE aluno_id = ? AND data = ?', (aluno['id'], hoje))
    cantina_checkin = cursor.fetchone()
    if cantina_checkin is not None:
        conn.close()
        # FIX: status mudado de ja_registrado para ja_almocou (alarme depende disso)
        return {'status': 'ja_almocou', 'aluno': aluno}
    
    # Tudo ok
    conn.close()
    return {'status': 'liberado', 'aluno': aluno}

def gerar_relatorio_portaria_hoje():
    """
    Retorna dados para relatório diário da portaria.
    """
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    
    # Total geral
    cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (hoje,))
    total_geral = cursor.fetchone()[0]
    
    # Detalhamento por turma
    cursor.execute('''
        SELECT a.turma, COUNT(*) as quantidade
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        WHERE cp.data = ?
        GROUP BY a.turma
        ORDER BY a.turma
    ''', (hoje,))
    rows = cursor.fetchall()
    detalhes_turma = [dict(row) for row in rows]
    
    # Detalhamento por turno
    cursor.execute('''
        SELECT a.turno, COUNT(*) as quantidade
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        WHERE cp.data = ?
        GROUP BY a.turno
        ORDER BY a.turno
    ''', (hoje,))
    rows = cursor.fetchall()
    detalhes_turno = [dict(row) for row in rows]
    
    conn.close()
    
    # Formatar detalhes para texto
    texto_detalhes = ''
    if detalhes_turma:
        texto_detalhes += 'Por turma:\n'
        for item in detalhes_turma:
            texto_detalhes += f"  {item['turma']}: {item['quantidade']} alunos\n"
    
    if detalhes_turno:
        texto_detalhes += 'Por turno:\n'
        for item in detalhes_turno:
            texto_detalhes += f"  {item['turno']}: {item['quantidade']} alunos\n"
    
    return {
        'total': total_geral,
        'detalhes_turma': detalhes_turma,
        'detalhes_turno': detalhes_turno,
        'texto_detalhes': texto_detalhes.strip()
    }

def relatorio_ja_enviado_hoje():
    """
    Verifica se já foi enviado relatório hoje.
    """
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    cursor.execute('SELECT id FROM relatorios_enviados WHERE data = ?', (hoje,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def registrar_relatorio_enviado(total_esperado):
    """
    Registra no banco que o relatório foi enviado hoje.
    """
    from datetime import datetime, date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    agora = datetime.now().isoformat(' ', 'seconds')
    try:
        cursor.execute('''
            INSERT INTO relatorios_enviados (data, total_esperado, enviado_em)
            VALUES (?, ?, ?)
        ''', (hoje, total_esperado, agora))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Já existe registro para hoje (UNIQUE constraint)
        conn.rollback()
        success = False
    finally:
        conn.close()
    return success

def enviar_relatorio_whatsapp_agora():
    """
    Gera e envia relatório diário via WhatsApp.
    Retorna (sucesso, mensagem).
    """
    from datetime import datetime
    # Verifica se já foi enviado hoje
    if relatorio_ja_enviado_hoje():
        return False, 'Relatório já enviado hoje.'
    
    # Gera dados
    relatorio = gerar_relatorio_portaria_hoje()
    total = relatorio['total']
    if total == 0:
        return False, 'Nenhum check-in registrado hoje. Relatório não enviado.'
    
    # Prepara mensagem para log
    hoje = datetime.now().strftime('%d/%m/%Y %H:%M')
    mensagem_log = f'''Relatório Cantina Escola - {hoje}
Previsão de almoços: {total} alunos
{relatorio.get('texto_detalhes', 'Sem detalhes')}
'''
    
    # Salva em arquivo (sempre, como fallback)
    try:
        with open('relatorios_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Data: {hoje}\n")
            f.write(f"Total: {total} alunos\n")
            f.write(mensagem_log)
            f.write(f"\n{'='*50}\n")
    except Exception as e:
        logger.error(f'Erro ao salvar relatório em arquivo: {e}')
    
    # Envia via WhatsApp
    from whatsapp_sender import enviar_relatorio_diario
    detalhes = relatorio['texto_detalhes'] if relatorio['texto_detalhes'] else None
    sucesso = enviar_relatorio_diario(total_esperado=total, detalhes=detalhes)
    
    if sucesso:
        # Registra envio
        registrar_relatorio_enviado(total)
        return True, f'Relatório enviado com sucesso. Total: {total} alunos.'
    else:
        # Mesmo com falha no WhatsApp, registra que o relatório foi gerado
        registrar_relatorio_enviado(total)
        return False, 'Relatório gerado e salvo em log, mas falha ao enviar via WhatsApp.'

# ============================================================================
# Funções para Dashboard Administrativo (Prompt 5)
# ============================================================================

def estatisticas_gerais():
    """
    Retorna estatísticas gerais para o dashboard.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Total de alunos ativos
    cursor.execute('SELECT COUNT(*) FROM alunos WHERE ativo = 1')
    total_alunos_ativos = cursor.fetchone()[0]
    
    # Total de alunos por turma
    cursor.execute('SELECT turma, COUNT(*) FROM alunos WHERE ativo = 1 GROUP BY turma ORDER BY turma')
    alunos_por_turma = [dict(turma=row[0], quantidade=row[1]) for row in cursor.fetchall()]
    
    # Total de alunos por turno
    cursor.execute('SELECT turno, COUNT(*) FROM alunos WHERE ativo = 1 GROUP BY turno ORDER BY turno')
    alunos_por_turno = [dict(turno=row[0], quantidade=row[1]) for row in cursor.fetchall()]
    
    # Check-ins portaria hoje
    from datetime import date
    hoje = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (hoje,))
    portaria_hoje = cursor.fetchone()[0]
    
    # Check-ins cantina hoje
    cursor.execute('SELECT COUNT(*) FROM checkin_cantina WHERE data = ?', (hoje,))
    cantina_hoje = cursor.fetchone()[0]
    
    # Alunos que fizeram portaria mas ainda não cantina (esperados para almoço)
    cursor.execute('''
        SELECT COUNT(DISTINCT cp.aluno_id)
        FROM checkin_portaria cp
        LEFT JOIN checkin_cantina cc ON cp.aluno_id = cc.aluno_id AND cp.data = cc.data
        WHERE cp.data = ? AND cc.id IS NULL
    ''', (hoje,))
    esperados_almoco = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_alunos_ativos': total_alunos_ativos,
        'alunos_por_turma': alunos_por_turma,
        'alunos_por_turno': alunos_por_turno,
        'portaria_hoje': portaria_hoje,
        'cantina_hoje': cantina_hoje,
        'esperados_almoco': esperados_almoco,
        'data_hoje': hoje
    }

def historico_checkins(dias=7):
    """
    Retorna histórico de check-ins dos últimos N dias para gráficos.
    """
    from datetime import date, timedelta
    conn = get_db()
    cursor = conn.cursor()
    
    historico = []
    for i in range(dias - 1, -1, -1):  # do mais antigo ao mais recente
        data = (date.today() - timedelta(days=i)).isoformat()
        
        cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (data,))
        portaria = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM checkin_cantina WHERE data = ?', (data,))
        cantina = cursor.fetchone()[0]
        
        # Número de alunos que fizeram portaria mas não cantina naquele dia
        cursor.execute('''
            SELECT COUNT(DISTINCT cp.aluno_id)
            FROM checkin_portaria cp
            LEFT JOIN checkin_cantina cc ON cp.aluno_id = cc.aluno_id AND cp.data = cc.data
            WHERE cp.data = ? AND cc.id IS NULL
        ''', (data,))
        sem_almoco = cursor.fetchone()[0]
        
        historico.append({
            'data': data,
            'portaria': portaria,
            'cantina': cantina,
            'sem_almoco': sem_almoco,
            'total_alunos': portaria  # equivalente a portaria, pois são os que planejaram almoçar
        })
    
    conn.close()
    return historico

def relatorio_detalhado(data_inicio=None, data_fim=None, turma=None, turno=None):
    """
    Gera relatório detalhado com filtros opcionais.
    """
    from datetime import date, timedelta
    conn = get_db()
    cursor = conn.cursor()
    
    # Define datas padrão (últimos 7 dias)
    if not data_inicio:
        data_inicio = (date.today() - timedelta(days=7)).isoformat()
    if not data_fim:
        data_fim = date.today().isoformat()
    
    # Base query
    query = '''
        SELECT 
            cp.data,
            a.turma,
            a.turno,
            COUNT(DISTINCT cp.aluno_id) as total_portaria,
            COUNT(DISTINCT cc.aluno_id) as total_cantina,
            GROUP_CONCAT(DISTINCT a.nome) as nomes_portaria
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        LEFT JOIN checkin_cantina cc ON cp.aluno_id = cc.aluno_id AND cp.data = cc.data
        WHERE cp.data BETWEEN ? AND ?
    '''
    params = [data_inicio, data_fim]
    
    if turma:
        query += ' AND a.turma = ?'
        params.append(turma)
    if turno:
        query += ' AND a.turno = ?'
        params.append(turno)
    
    query += '''
        GROUP BY cp.data, a.turma, a.turno
        ORDER BY cp.data DESC, a.turma, a.turno
    '''
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    resultado = []
    for row in rows:
        resultado.append({
            'data': row[0],
            'turma': row[1],
            'turno': row[2],
            'total_portaria': row[3],
            'total_cantina': row[4],
            'nomes_portaria': row[5].split(',') if row[5] else []
        })
    
    # Totais agregados
    query_totais = '''
        SELECT 
            COUNT(DISTINCT cp.aluno_id) as alunos_unicos_portaria,
            COUNT(DISTINCT cc.aluno_id) as alunos_unicos_cantina,
            COUNT(DISTINCT CASE WHEN cc.id IS NULL THEN cp.aluno_id END) as alunos_sem_almoco
        FROM checkin_portaria cp
        LEFT JOIN checkin_cantina cc ON cp.aluno_id = cc.aluno_id AND cp.data = cc.data
        WHERE cp.data BETWEEN ? AND ?
    '''
    params_totais = [data_inicio, data_fim]
    
    if turma or turno:
        query_totais = query_totais.replace('WHERE', 'JOIN alunos a ON cp.aluno_id = a.id WHERE')
        if turma:
            query_totais += ' AND a.turma = ?'
            params_totais.append(turma)
        if turno:
            query_totais += ' AND a.turno = ?'
            params_totais.append(turno)
    
    cursor.execute(query_totais, params_totais)
    totais_row = cursor.fetchone()
    
    conn.close()
    
    return {
        'periodo': {'inicio': data_inicio, 'fim': data_fim},
        'filtros': {'turma': turma, 'turno': turno},
        'detalhes': resultado,
        'totais': {
            'alunos_unicos_portaria': totais_row[0] if totais_row else 0,
            'alunos_unicos_cantina': totais_row[1] if totais_row else 0,
            'alunos_sem_almoco': totais_row[2] if totais_row else 0
        }
    }


# ============================================================================
# Novas funções para Dashboard Avançado (Prompt 5)
# ============================================================================

def dashboard_dados():
    """
    Retorna dados completos para o dashboard administrativo.
    Inclui estatísticas para os 4 cards, dados para gráficos e últimas atividades.
    """
    stats = estatisticas_gerais()
    
    # Dados para os cards específicos
    portaria_hoje = stats['portaria_hoje']
    cantina_hoje = stats['cantina_hoje']
    esperados_almoco = stats['esperados_almoco']
    total_alunos_ativos = stats['total_alunos_ativos']
    
    # Card 1: Progresso de almoços hoje (barra de progresso)
    if portaria_hoje > 0:
        progresso_percent = int((cantina_hoje / portaria_hoje) * 100)
    else:
        progresso_percent = 0
    
    # Card 2: Desperdício evitado
    # Suposição: desperdício evitado = alunos que almoçaram vs. total que poderia almoçar
    # Fórmula: (cantina_hoje / portaria_hoje) * 100, mas invertido para mostrar "evitado"
    if portaria_hoje > 0:
        desperdicio_evitado_percent = int((cantina_hoje / portaria_hoje) * 100)
        desperdicio_potencial = portaria_hoje - cantina_hoje
    else:
        desperdicio_evitado_percent = 100
        desperdicio_potencial = 0
    
    # Card 3: Check-ins portaria (já existe)
    # Card 4: Check-ins cantina (já existe)
    
    # Dados para gráfico de almoços por turma hoje
    turmas_almoco = almocos_por_turma_hoje()
    
    # Histórico semanal para gráfico de barras
    historico_semanal = historico_almoco_semanal()
    
    # Últimas atividades
    ultimas_ativ = ultimas_atividades(limite=10)
    
    return {
        'cards': {
            'progresso_almoco': {
                'valor_atual': cantina_hoje,
                'valor_total': portaria_hoje,
                'percentual': progresso_percent,
                'label': f'{cantina_hoje}/{portaria_hoje}'
            },
            'desperdicio_evitado': {
                'percentual': desperdicio_evitado_percent,
                'potencial': desperdicio_potencial,
                'label': f'{desperdicio_evitado_percent}% evitado'
            },
            'checkins_portaria': {
                'valor': portaria_hoje,
                'label': 'Check-ins Portaria'
            },
            'checkins_cantina': {
                'valor': cantina_hoje,
                'label': 'Check-ins Cantina'
            }
        },
        'grafico_turmas': turmas_almoco,
        'historico_semanal': historico_semanal,
        'ultimas_atividades': ultimas_ativ,
        'estatisticas_gerais': stats
    }

def relatorio_detalhado_data(data):
    """
    Gera relatório detalhado para uma data específica.
    Retorna 4 tabelas: check-ins portaria, check-ins cantina, desistências, liberações forçadas.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Check-ins portaria na data
    cursor.execute('''
        SELECT a.id, a.matricula, a.nome, a.turma, a.turno, cp.hora_checkin
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        WHERE cp.data = ?
        ORDER BY cp.hora_checkin
    ''', (data,))
    rows = cursor.fetchall()
    checkins_portaria = [dict(row) for row in rows]
    
    # 2. Check-ins cantina na data
    cursor.execute('''
        SELECT a.id, a.matricula, a.nome, a.turma, a.turno, cc.hora_almoco
        FROM checkin_cantina cc
        JOIN alunos a ON cc.aluno_id = a.id
        WHERE cc.data = ?
        ORDER BY cc.hora_almoco
    ''', (data,))
    rows = cursor.fetchall()
    checkins_cantina = [dict(row) for row in rows]
    
    # 3. Desistências (fizeram portaria mas não cantina)
    cursor.execute('''
        SELECT a.id, a.matricula, a.nome, a.turma, a.turno, cp.hora_checkin
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        LEFT JOIN checkin_cantina cc ON cp.aluno_id = cc.aluno_id AND cp.data = cc.data
        WHERE cp.data = ? AND cc.id IS NULL
        ORDER BY cp.hora_checkin
    ''', (data,))
    rows = cursor.fetchall()
    desistencias = [dict(row) for row in rows]
    
    # 4. Liberações forçadas (não implementado ainda - placeholder)
    # Por enquanto, lista vazia
    liberacoes_forcadas = []
    
    # Totais resumidos
    total_portaria = len(checkins_portaria)
    total_cantina = len(checkins_cantina)
    total_desistencias = len(desistencias)
    total_liberacoes = len(liberacoes_forcadas)
    
    conn.close()
    
    return {
        'data': data,
        'tabelas': {
            'checkins_portaria': checkins_portaria,
            'checkins_cantina': checkins_cantina,
            'desistencias': desistencias,
            'liberacoes_forcadas': liberacoes_forcadas
        },
        'totais': {
            'portaria': total_portaria,
            'cantina': total_cantina,
            'desistencias': total_desistencias,
            'liberacoes_forcadas': total_liberacoes
        }
    }

def historico_almoco_semanal(dias=7):
    """
    Retorna histórico de almoços nos últimos N dias para gráfico de barras.
    Formato otimizado para Chart.js.
    """
    from datetime import date, timedelta
    
    conn = get_db()
    cursor = conn.cursor()
    
    datas = []
    portaria_vals = []
    cantina_vals = []
    
    for i in range(dias - 1, -1, -1):  # do mais antigo ao mais recente
        data = (date.today() - timedelta(days=i)).isoformat()
        datas.append(data)
        
        cursor.execute('SELECT COUNT(*) FROM checkin_portaria WHERE data = ?', (data,))
        portaria = cursor.fetchone()[0]
        portaria_vals.append(portaria)
        
        cursor.execute('SELECT COUNT(*) FROM checkin_cantina WHERE data = ?', (data,))
        cantina = cursor.fetchone()[0]
        cantina_vals.append(cantina)
    
    conn.close()
    
    return {
        'datas': datas,
        'portaria': portaria_vals,
        'cantina': cantina_vals
    }

def almocos_por_turma_hoje():
    """
    Retorna contagem de almoços por turma no dia atual para gráfico de pizza.
    """
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    
    cursor.execute('''
        SELECT a.turma, COUNT(*) as quantidade
        FROM checkin_cantina cc
        JOIN alunos a ON cc.aluno_id = a.id
        WHERE cc.data = ?
        GROUP BY a.turma
        ORDER BY a.turma
    ''', (hoje,))
    rows = cursor.fetchall()
    
    turmas = []
    quantidades = []
    cores = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
        '#9966FF', '#FF9F40', '#8AC926', '#1982C4'
    ]
    
    for i, row in enumerate(rows):
        turmas.append(row[0])
        quantidades.append(row[1])
    
    conn.close()
    
    return {
        'turmas': turmas,
        'quantidades': quantidades,
        'cores': cores[:len(turmas)]
    }

def ultimas_atividades(limite=10):
    """
    Retorna as últimas atividades do sistema, intercalando portaria e cantina.
    """
    from datetime import date
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()
    
    # Últimos check-ins portaria
    cursor.execute('''
        SELECT 'portaria' as tipo, a.nome, a.turma, cp.hora_checkin as hora
        FROM checkin_portaria cp
        JOIN alunos a ON cp.aluno_id = a.id
        WHERE cp.data = ?
        ORDER BY cp.hora_checkin DESC
        LIMIT ?
    ''', (hoje, limite))
    portaria = [dict(row) for row in cursor.fetchall()]
    
    # Últimos check-ins cantina
    cursor.execute('''
        SELECT 'cantina' as tipo, a.nome, a.turma, cc.hora_almoco as hora
        FROM checkin_cantina cc
        JOIN alunos a ON cc.aluno_id = a.id
        WHERE cc.data = ?
        ORDER BY cc.hora_almoco DESC
        LIMIT ?
    ''', (hoje, limite))
    cantina = [dict(row) for row in cursor.fetchall()]
    
    # Intercalar as atividades (merge por hora)
    todas = []
    i = j = 0
    while len(todas) < limite and (i < len(portaria) or j < len(cantina)):
        if i < len(portaria) and j < len(cantina):
            # Comparar horas (formato 'YYYY-MM-DD HH:MM:SS')
            if portaria[i]['hora'] >= cantina[j]['hora']:
                todas.append(portaria[i])
                i += 1
            else:
                todas.append(cantina[j])
                j += 1
        elif i < len(portaria):
            todas.append(portaria[i])
            i += 1
        else:
            todas.append(cantina[j])
            j += 1
    
    # Formatar hora para exibição (remover data se for hoje)
    for atividade in todas:
        hora_str = atividade['hora']
        if hora_str.startswith(hoje + ' '):
            atividade['hora_display'] = hora_str[len(hoje)+1:]
        else:
            atividade['hora_display'] = hora_str
    
    conn.close()
    return todas[:limite]

# ============================================================================
# Funções de configuração do sistema
# ============================================================================

def get_config(chave, default=None):
    """Retorna o valor de uma configuração pelo seu chave."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default


def set_config(chave, valor, descricao=None):
    """Define o valor de uma configuração, criando ou atualizando."""
    conn = get_db()
    cursor = conn.cursor()
    if descricao:
        cursor.execute('''
            INSERT INTO configuracoes (chave, valor, descricao) 
            VALUES (?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET 
                valor = excluded.valor,
                descricao = excluded.descricao,
                atualizado_em = CURRENT_TIMESTAMP
        ''', (chave, valor, descricao))
    else:
        cursor.execute('''
            INSERT INTO configuracoes (chave, valor) 
            VALUES (?, ?)
            ON CONFLICT(chave) DO UPDATE SET 
                valor = excluded.valor,
                atualizado_em = CURRENT_TIMESTAMP
        ''', (chave, valor))
    conn.commit()
    conn.close()


def get_all_config():
    """Retorna todas as configurações como uma lista de dicionários."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT chave, valor, descricao, atualizado_em FROM configuracoes ORDER BY chave')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'chave': row[0],
            'valor': row[1],
            'descricao': row[2],
            'atualizado_em': row[3]
        }
        for row in rows
    ]