import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, Response
from pathlib import Path
import os
import atexit
import csv
import io
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import settings
from config import (
    SECRET_KEY, TURMAS, TURNOS, WHATSAPP_SEND_HOUR, WHATSAPP_SEND_MINUTE,
    WHATSAPP_ENABLED, REPORT_ADMIN_PHONE, QRCODE_DIR
)
from database import init_db, get_db
from models import (
    cadastrar_aluno, listar_alunos, buscar_aluno_por_matricula, 
    editar_aluno, desativar_aluno, reativar_aluno, 
    registrar_checkin_portaria, contar_checkins_portaria_hoje,
    registrar_checkin_cantina, contar_checkins_cantina_hoje, verificar_estado_aluno_para_almoco,
    gerar_relatorio_portaria_hoje, relatorio_ja_enviado_hoje,
    registrar_relatorio_enviado, enviar_relatorio_whatsapp_agora,
      estatisticas_gerais, historico_checkins, relatorio_detalhado,
      get_config, set_config, get_all_config, estatisticas_almoco_hoje,
      dashboard_dados, relatorio_detalhado_data, historico_almoco_semanal,
      almocos_por_turma_hoje, ultimas_atividades
)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

init_db()

# Agendador de relatório automático
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    scheduler = BackgroundScheduler()
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    def enviar_relatorio_agendado():
        """Função chamada pelo agendador para enviar relatório diário."""
        with app.app_context():
            try:
                sucesso, mensagem = enviar_relatorio_whatsapp_agora()
                app.logger.info(f'Relatório automático: {mensagem}')
            except Exception as e:
                app.logger.error(f'Erro no relatório automático: {e}')

    # Agenda o envio para 8h todos os dias
    trigger = CronTrigger(hour=WHATSAPP_SEND_HOUR, minute=WHATSAPP_SEND_MINUTE)
    scheduler.add_job(
        func=enviar_relatorio_agendado,
        trigger=trigger,
        id='relatorio_diario',
        name='Envio automático de relatório às 8h',
        replace_existing=True,
        misfire_grace_time=3600  # Se o servidor ligar atrasado, ainda executa
    )

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard administrativo com estatísticas e gráficos."""
    dados = dashboard_dados()
    dias_historico = int(get_config('dias_historico', 7))
    historico = historico_checkins(dias_historico)  # mantido para compatibilidade
    return render_template('dashboard.html', 
                           stats=dados['estatisticas_gerais'], 
                           historico=historico,
                           turmas=TURMAS,
                           turnos=TURNOS,
                           dashboard=dados)

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint para dados do dashboard (usado para auto-refresh AJAX)."""
    dados = dashboard_dados()
    return jsonify(dados)

@app.route('/api/relatorio/<data>')
def api_relatorio_data(data):
    """API endpoint para relatório detalhado de uma data específica."""
    relatorio = relatorio_detalhado_data(data)
    return jsonify(relatorio)

@app.route('/relatorios/<data>')
def relatorio_por_dia(data):
    """Página de relatório detalhado para uma data específica."""
    relatorio = relatorio_detalhado_data(data)
    hoje = date.today().isoformat()
    return render_template('relatorio_por_dia.html',
                           relatorio=relatorio,
                           data=data,
                           hoje=hoje)

@app.route('/relatorio')
def relatorio_detalhado_view():
    """Página de relatório detalhado com filtros."""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    turma = request.args.get('turma')
    turno = request.args.get('turno')
    
    relatorio = relatorio_detalhado(data_inicio, data_fim, turma, turno)
    hoje = date.today().isoformat()
    
    return render_template('relatorio_detalhado.html',
                           relatorio=relatorio,
                           turmas=TURMAS,
                           turnos=TURNOS,
                           hoje=hoje)

@app.route('/relatorio/exportar/csv')
def exportar_relatorio_csv():
    """Exporta o relatório detalhado como CSV."""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    turma = request.args.get('turma')
    turno = request.args.get('turno')
    
    relatorio = relatorio_detalhado(data_inicio, data_fim, turma, turno)
    
    # Criar CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['Data', 'Turma', 'Turno', 'Total Portaria', 'Total Cantina', 'Alunos Portaria'])
    
    # Dados
    for item in relatorio['detalhes']:
        nomes_portaria = ', '.join(item['nomes_portaria']) if item['nomes_portaria'] else ''
        writer.writerow([
            item['data'],
            item['turma'],
            item['turno'],
            item['total_portaria'],
            item['total_cantina'],
            nomes_portaria
        ])
    
    # Totais (linhas adicionais)
    writer.writerow([])  # linha vazia
    writer.writerow(['TOTAIS DO PERÍODO:'])
    writer.writerow(['Alunos únicos portaria:', relatorio['totais']['alunos_unicos_portaria']])
    writer.writerow(['Alunos únicos cantina:', relatorio['totais']['alunos_unicos_cantina']])
    writer.writerow(['Alunos sem almoço:', relatorio['totais']['alunos_sem_almoco']])
    writer.writerow(['Período:', f"{relatorio['periodo']['inicio']} a {relatorio['periodo']['fim']}"])
    
    # Preparar resposta
    output.seek(0)
    filename = f"relatorio_cantina_{relatorio['periodo']['inicio']}_{relatorio['periodo']['fim']}.csv"
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/relatorio/exportar/pdf')
def exportar_relatorio_pdf():
    """Exporta o relatório detalhado como PDF."""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    turma = request.args.get('turma')
    turno = request.args.get('turno')
    
    relatorio = relatorio_detalhado(data_inicio, data_fim, turma, turno)
    
    # Criar PDF em memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    title = Paragraph(f"Relatório da Cantina Escolar", title_style)
    elements.append(title)
    
    # Período
    periodo = Paragraph(
        f"<b>Período:</b> {relatorio['periodo']['inicio']} a {relatorio['periodo']['fim']}",
        styles['Normal']
    )
    elements.append(periodo)
    
    # Filtros
    filtros_text = []
    if relatorio['filtros']['turma']:
        filtros_text.append(f"Turma: {relatorio['filtros']['turma']}")
    if relatorio['filtros']['turno']:
        filtros_text.append(f"Turno: {relatorio['filtros']['turno']}")
    
    if filtros_text:
        filtros = Paragraph(
            f"<b>Filtros aplicados:</b> {'; '.join(filtros_text)}",
            styles['Normal']
        )
        elements.append(filtros)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabela de dados
    if relatorio['detalhes']:
        # Cabeçalho
        data = [['Data', 'Turma', 'Turno', 'Portaria', 'Cantina', 'Alunos Portaria']]
        
        # Linhas
        for item in relatorio['detalhes']:
            nomes_portaria = ', '.join(item['nomes_portaria'][:3])  # Limitar a 3 nomes
            if len(item['nomes_portaria']) > 3:
                nomes_portaria += f"... (+{len(item['nomes_portaria']) - 3})"
            
            data.append([
                item['data'],
                item['turma'],
                item['turno'],
                str(item['total_portaria']),
                str(item['total_cantina']),
                nomes_portaria
            ])
        
        table = Table(data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 7*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
    else:
        no_data = Paragraph("<b>Nenhum dado encontrado para o período e filtros selecionados.</b>", 
                           styles['Normal'])
        elements.append(no_data)
    
    # Totais
    elements.append(Spacer(1, 0.5*cm))
    totais_title = Paragraph("<b>Resumo do Período:</b>", styles['Heading3'])
    elements.append(totais_title)
    
    totais_data = [
        ['Alunos únicos na portaria:', str(relatorio['totais']['alunos_unicos_portaria'])],
        ['Alunos únicos na cantina:', str(relatorio['totais']['alunos_unicos_cantina'])],
        ['Alunos que não almoçaram:', str(relatorio['totais']['alunos_sem_almoco'])],
    ]
    
    totais_table = Table(totais_data, colWidths=[8*cm, 3*cm])
    totais_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ]))
    elements.append(totais_table)
    
    # Data de geração
    gerado_em = Paragraph(
        f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
        styles['Italic']
    )
    elements.append(Spacer(1, 1*cm))
    elements.append(gerado_em)
    
    # Construir PDF
    doc.build(elements)
    
    buffer.seek(0)
    filename = f"relatorio_cantina_{relatorio['periodo']['inicio']}_{relatorio['periodo']['fim']}.pdf"
    
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/alunos/qrcodes/pdf')
def imprimir_qrcodes_alunos():
    """Gera PDF com todos os QR codes dos alunos ativos para impressão em lote."""
    # Obter alunos ativos
    alunos = listar_alunos(ativo=True)
    
    if not alunos:
        flash('Nenhum aluno ativo encontrado.', 'warning')
        return redirect(url_for('listar_alunos_view'))
    
    # Criar PDF em memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20
    )
    title = Paragraph(f"QR Codes dos Alunos - Sistema da Cantina", title_style)
    elements.append(title)
    
    # Data de geração
    gerado_em = Paragraph(
        f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Total de {len(alunos)} aluno(s) ativo(s)</i>",
        styles['Italic']
    )
    elements.append(gerado_em)
    elements.append(Spacer(1, 1*cm))
    
    # Organizar alunos em grade 2x2 (4 por página)
    # Tamanho máximo da imagem do QR code: 5cm x 5cm
    qr_size = 5*cm
    
    # Processar alunos em grupos de 4
    for i in range(0, len(alunos), 4):
        grupo = alunos[i:i+4]
        
        # Criar uma tabela 2x2 para este grupo
        data = []
        for j in range(0, len(grupo), 2):
            row = []
            for k in range(2):
                idx = j + k
                if idx < len(grupo):
                    aluno = grupo[idx]
                    # Caminho do QR code
                    qr_path = Path(QRCODE_DIR) / f"{aluno['matricula']}.png"
                    
                    # Verificar se arquivo existe
                    if qr_path.exists():
                        # Criar célula com imagem e texto
                        cell_content = [
                            Image(str(qr_path), width=qr_size, height=qr_size),
                            Paragraph(f"<b>{aluno['nome']}</b>", styles['Normal']),
                            Paragraph(f"Matrícula: {aluno['matricula']}", styles['Small']),
                            Paragraph(f"Turma: {aluno['turma']} - Turno: {aluno['turno']}", styles['Small'])
                        ]
                        # Usar uma tabela interna para centralizar conteúdo
                        from reportlab.platypus.flowables import KeepTogether
                        inner_table = Table([[cell_content]], colWidths=[qr_size])
                        inner_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        row.append(inner_table)
                    else:
                        # QR code não encontrado
                        row.append(Paragraph(f"QR code não gerado para {aluno['matricula']}", styles['Normal']))
                else:
                    # Célula vazia
                    row.append('')
            data.append(row)
        
        # Criar tabela para o grupo
        if data:
            table = Table(data, colWidths=[qr_size, qr_size])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(table)
            
            # Adicionar espaço entre grupos (exceto no último)
            if i + 4 < len(alunos):
                elements.append(Spacer(1, 1*cm))
    
    # Rodapé
    elements.append(Spacer(1, 1*cm))
    rodape = Paragraph(
        "<i>Use este documento para imprimir e recortar os QR codes. Cada aluno deve ter seu QR code pessoal.</i>",
        styles['Italic']
    )
    elements.append(rodape)
    
    # Construir PDF
    doc.build(elements)
    
    buffer.seek(0)
    filename = f"qrcodes_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/api/historico')
def api_historico():
    """API que retorna dados históricos para gráficos (JSON)."""
    dias = request.args.get('dias', default=7, type=int)
    historico = historico_checkins(dias)
    return jsonify(historico)

@app.route('/alunos')
def listar_alunos_view():
    filtro_turma = request.args.get('turma')
    filtro_turno = request.args.get('turno')
    
    alunos = listar_alunos(filtro_turma, filtro_turno, ativo=None)
    
    return render_template('lista_alunos.html', 
                           alunos=alunos, 
                           turmas=TURMAS, 
                           turnos=TURNOS,
                           filtro_turma=filtro_turma,
                           filtro_turno=filtro_turno)

@app.route('/alunos/cadastro', methods=['GET', 'POST'])
def cadastro_aluno():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        matricula = request.form['matricula'].strip()
        turma = request.form['turma']
        turno = request.form['turno']
        
        if not nome or not matricula:
            flash('Nome e matrícula são obrigatórios.', 'danger')
            return render_template('cadastro.html', turmas=TURMAS, turnos=TURNOS)
        
        try:
            aluno = cadastrar_aluno(nome, matricula, turma, turno)
            flash(f'Aluno {aluno["nome"]} cadastrado com sucesso! QR Code gerado.', 'success')
            flash(f'Para baixar o QR Code, <a href="{url_for("download_qrcode", matricula=aluno["matricula"])}" class="alert-link">clique aqui</a>.', 'info')
            return redirect(url_for('listar_alunos_view'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('cadastro.html', turmas=TURMAS, turnos=TURNOS)
        except Exception as e:
            flash(f'Erro interno: {e}', 'danger')
            return render_template('cadastro.html', turmas=TURMAS, turnos=TURNOS)
    
    return render_template('cadastro.html', turmas=TURMAS, turnos=TURNOS)

@app.route('/alunos/qrcode/<matricula>')
def download_qrcode(matricula):
    from config import QRCODE_DIR
    filename = QRCODE_DIR / f'{matricula}.png'
    if not filename.exists():
        flash('QR Code não encontrado.', 'danger')
        return redirect(url_for('listar_alunos_view'))
    return send_file(filename, as_attachment=True, download_name=f'QRCode_{matricula}.png')

@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno_view(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alunos WHERE id = ?', (id,))
    aluno = cursor.fetchone()
    conn.close()
    
    if aluno is None:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('listar_alunos_view'))
    
    aluno = dict(aluno)
    
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        turma = request.form['turma']
        turno = request.form['turno']
        
        if not nome:
            flash('Nome é obrigatório.', 'danger')
            return render_template('editar_aluno.html', aluno=aluno, turmas=TURMAS, turnos=TURNOS)
        
        try:
            editar_aluno(id, nome, turma, turno)
            flash('Dados do aluno atualizados com sucesso.', 'success')
            return redirect(url_for('listar_alunos_view'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('editar_aluno.html', aluno=aluno, turmas=TURMAS, turnos=TURNOS)
    
    return render_template('editar_aluno.html', aluno=aluno, turmas=TURMAS, turnos=TURNOS)

@app.route('/alunos/desativar/<int:id>', methods=['POST'])
def desativar_aluno_view(id):
    if request.form.get('confirm') == 'true':
        desativar_aluno(id)
        flash('Aluno desativado com sucesso.', 'success')
    return redirect(url_for('listar_alunos_view'))

@app.route('/alunos/reativar/<int:id>', methods=['POST'])
def reativar_aluno_view(id):
    if request.form.get('confirm') == 'true':
        reativar_aluno(id)
        flash('Aluno reativado com sucesso.', 'success')
    return redirect(url_for('listar_alunos_view'))

@app.route('/portaria')
def portaria():
    return render_template('portaria.html')

@app.route('/api/checkin-portaria', methods=['POST'])
def api_checkin_portaria():
    data = request.get_json()
    if not data or 'qrcode_hash' not in data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    resultado = registrar_checkin_portaria(data['qrcode_hash'])
    return jsonify(resultado)

@app.route('/api/portaria/contagem-hoje')
def api_portaria_contagem_hoje():
    total = contar_checkins_portaria_hoje()
    hoje = date.today().isoformat()
    return jsonify({'total': total, 'data': hoje})

# Rotas para o scanner da cantina
@app.route('/cantina')
def cantina():
    alarme_som = get_config('alarme_som', 'true') == 'true'
    alarme_visual = get_config('alarme_visual', 'true') == 'true'
    return render_template('cantina.html', alarme_som=alarme_som, alarme_visual=alarme_visual)

@app.route('/api/checkin-cantina', methods=['POST'])
def api_checkin_cantina():
    data = request.get_json()
    if not data or 'qrcode_hash' not in data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    resultado = registrar_checkin_cantina(data['qrcode_hash'])
    return jsonify(resultado)

@app.route('/api/cantina/contagem-hoje')
def api_cantina_contagem_hoje():
    total = contar_checkins_cantina_hoje()
    hoje = date.today().isoformat()
    return jsonify({'total': total, 'data': hoje})

@app.route('/api/cantina/verificar/<qrcode_hash>')
def api_cantina_verificar(qrcode_hash):
    resultado = verificar_estado_aluno_para_almoco(qrcode_hash)
    return jsonify(resultado)

@app.route('/api/cantina/estatisticas')
def api_cantina_estatisticas():
    # FIX: rota faltante que causava 404
    stats = estatisticas_almoco_hoje()
    return jsonify(stats)

# Rotas de administração do relatório
@app.route('/admin/relatorio')
def admin_relatorio():
    """Página de administração do relatório."""
    relatorio = gerar_relatorio_portaria_hoje()
    ja_enviado = relatorio_ja_enviado_hoje()
    config_vars = {
        'WHATSAPP_ENABLED': WHATSAPP_ENABLED,
        'REPORT_ADMIN_PHONE': REPORT_ADMIN_PHONE,
        'WHATSAPP_SEND_HOUR': WHATSAPP_SEND_HOUR,
        'WHATSAPP_SEND_MINUTE': WHATSAPP_SEND_MINUTE
    }
    return render_template('admin_relatorio.html',
                           relatorio=relatorio,
                           ja_enviado=ja_enviado,
                           turmas=TURMAS,
                           turnos=TURNOS,
                           config=config_vars)

@app.route('/admin/relatorio/enviar', methods=['POST'])
def admin_relatorio_enviar():
    """Envia manualmente o relatório diário."""
    sucesso, mensagem = enviar_relatorio_whatsapp_agora()
    flash(mensagem, 'success' if sucesso else 'danger')
    return redirect(url_for('admin_relatorio'))

@app.route('/api/relatorio/gerar-agora', methods=['POST'])
def api_relatorio_gerar_agora():
    """Gera relatório agora (para teste manual)."""
    try:
        sucesso, mensagem = enviar_relatorio_whatsapp_agora()
        return jsonify({
            'sucesso': sucesso,
            'mensagem': mensagem
        })
    except Exception as e:
        app.logger.error(f'Erro ao gerar relatório: {e}')
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/whatsapp/teste', methods=['POST'])
def api_whatsapp_teste():
    """Envia mensagem de teste via WhatsApp (CallMeBot)."""
    from whatsapp_sender import enviar_whatsapp_callmebot
    import json as _json
    try:
        config_path = Path(__file__).parent / 'config_escola.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = _json.load(f)
        wa = cfg.get('whatsapp', {})
        phone = wa.get('numero_telefone', '')
        apikey = wa.get('callmebot_apikey', '')
        if not phone or not apikey:
            return jsonify({'sucesso': False, 'mensagem': 'Phone ou API key não configurados.'}), 400
        msg = f"🧪 Teste do Sistema Cantina - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\nSe você recebeu esta mensagem, a integração está funcionando!"
        ok = enviar_whatsapp_callmebot(phone, apikey, msg)
        return jsonify({'sucesso': ok, 'mensagem': 'Mensagem enviada!' if ok else 'Falha ao enviar.'})
    except Exception as e:
        app.logger.error(f'Erro no teste WhatsApp: {e}')
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@app.route('/admin/configuracoes', methods=['GET', 'POST'])
def admin_configuracoes():
    """Página de administração de configurações do sistema (JSON-based)."""
    # Sincronizar do banco para JSON na primeira execução
    if not settings.CONFIG_JSON_PATH.exists():
        settings.migrate_from_database()
    
    if request.method == 'POST':
        try:
            # Carregar configurações atuais
            current = settings.load_settings()
            
            # Atualizar valores do formulário
            current['escola']['nome'] = request.form.get('escola_nome', '').strip()
            current['whatsapp']['habilitado'] = request.form.get('whatsapp_habilitado') == 'true'
            current['whatsapp']['horario_envio'] = request.form.get('whatsapp_horario', '08:00').strip()
            current['whatsapp']['grupo_id'] = request.form.get('whatsapp_grupo_id', '').strip()
            current['whatsapp']['metodo'] = request.form.get('whatsapp_metodo', 'pywhatkit').strip()
            current['whatsapp']['numero_telefone'] = request.form.get('whatsapp_numero', '').strip()
            current['sistema']['alarme_som'] = request.form.get('alarme_som') == 'true'
            current['sistema']['alarme_visual'] = request.form.get('alarme_visual') == 'true'
            try:
                current['sistema']['dias_historico'] = int(request.form.get('dias_historico', 7))
            except ValueError:
                current['sistema']['dias_historico'] = 7
            
            # Processar turmas (textarea, uma por linha)
            turmas_text = request.form.get('turmas_disponiveis', '').strip()
            turmas = [t.strip() for t in turmas_text.split('\n') if t.strip()]
            if turmas:
                current['escola']['turmas'] = turmas
            
            # Processar turnos (textarea, uma por linha)
            turnos_text = request.form.get('turnos_disponiveis', '').strip()
            turnos = [t.strip() for t in turnos_text.split('\n') if t.strip()]
            if turnos:
                current['escola']['turnos'] = turnos
            
            # Salvar configurações
            if settings.save_settings(current):
                flash('Configurações salvas com sucesso no arquivo JSON!', 'success')
            else:
                flash('Erro ao salvar configurações no arquivo JSON.', 'danger')
            
            # Atualizar variáveis globais (recarregar)
            settings.SETTINGS = current
        except Exception as e:
            flash(f'Erro ao processar configurações: {e}', 'danger')
        
        return redirect(url_for('admin_configuracoes'))
    
    # Carregar configurações para exibição
    config_data = settings.load_settings()
    return render_template('configuracoes.html', config=config_data)

@app.route('/configuracoes')
def configuracoes():
    """Alias para a página de configurações."""
    return redirect(url_for('admin_configuracoes'))

@app.route('/relatorios/<data>/exportar')
def exportar_relatorio_diario(data):
    """Exporta relatório de um dia específico como CSV ou PDF."""
    formato = request.args.get('formato', 'csv').lower()
    
    # Validar formato
    if formato not in ['csv', 'pdf']:
        flash('Formato inválido. Use "csv" ou "pdf".', 'danger')
        return redirect(url_for('relatorio_por_dia', data=data))
    
    # Obter relatório para a data (usando relatório detalhado por turma/turno)
    relatorio = relatorio_detalhado(data, data, None, None)
    
    # FIX: garantir que as chaves 'detalhes' e 'totais' existem no relatório
    if 'detalhes' not in relatorio:
        relatorio['detalhes'] = []
    if 'totais' not in relatorio:
        relatorio['totais'] = {
            'alunos_unicos_portaria': 0,
            'alunos_unicos_cantina': 0,
            'alunos_sem_almoco': 0
        }
    
    if formato == 'csv':
        # Criar CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Data', 'Turma', 'Turno', 'Total Portaria', 'Total Cantina', 'Alunos Portaria'])
        
        # Dados
        for item in relatorio['detalhes']:
            nomes_portaria = ', '.join(item['nomes_portaria']) if item['nomes_portaria'] else ''
            writer.writerow([
                item['data'],
                item['turma'],
                item['turno'],
                item['total_portaria'],
                item['total_cantina'],
                nomes_portaria
            ])
        
        # Totais
        writer.writerow([])
        writer.writerow(['TOTAIS DO DIA:'])
        writer.writerow(['Alunos únicos portaria:', relatorio['totais']['alunos_unicos_portaria']])
        writer.writerow(['Alunos únicos cantina:', relatorio['totais']['alunos_unicos_cantina']])
        writer.writerow(['Alunos sem almoço:', relatorio['totais']['alunos_sem_almoco']])
        
        output.seek(0)
        filename = f"relatorio_cantina_{data}.csv"
        
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    
    else:  # PDF
        # Criar PDF em memória
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=2*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        title = Paragraph(f"Relatório da Cantina Escolar - {data}", title_style)
        elements.append(title)
        
        # Data
        periodo = Paragraph(f"<b>Data:</b> {data}", styles['Normal'])
        elements.append(periodo)
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela de dados
        if relatorio['detalhes']:
            data_table = [['Data', 'Turma', 'Turno', 'Portaria', 'Cantina', 'Alunos Portaria']]
            for item in relatorio['detalhes']:
                nomes_portaria = ', '.join(item['nomes_portaria'][:3])
                if len(item['nomes_portaria']) > 3:
                    nomes_portaria += f"... (+{len(item['nomes_portaria']) - 3})"
                data_table.append([
                    item['data'],
                    item['turma'],
                    item['turno'],
                    str(item['total_portaria']),
                    str(item['total_cantina']),
                    nomes_portaria
                ])
            
            table = Table(data_table, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 7*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('ALIGN', (5, 1), (5, -1), 'LEFT'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.5*cm))
        else:
            no_data = Paragraph("<b>Nenhum dado encontrado para esta data.</b>", styles['Normal'])
            elements.append(no_data)
        
        # Totais
        elements.append(Spacer(1, 0.5*cm))
        totais_title = Paragraph("<b>Resumo do Dia:</b>", styles['Heading3'])
        elements.append(totais_title)
        
        totais_data = [
            ['Alunos únicos na portaria:', str(relatorio['totais']['alunos_unicos_portaria'])],
            ['Alunos únicos na cantina:', str(relatorio['totais']['alunos_unicos_cantina'])],
            ['Alunos que não almoçaram:', str(relatorio['totais']['alunos_sem_almoco'])],
        ]
        
        totais_table = Table(totais_data, colWidths=[8*cm, 3*cm])
        totais_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        elements.append(totais_table)
        
        # Data de geração
        gerado_em = Paragraph(
            f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
            styles['Italic']
        )
        elements.append(Spacer(1, 1*cm))
        elements.append(gerado_em)
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        filename = f"relatorio_cantina_{data}.pdf"
        
        return Response(
            buffer,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

@app.route('/alunos/imprimir-qrcodes')
def imprimir_qrcodes_html():
    """Página HTML otimizada para impressão em lote de QR codes."""
    turma = request.args.get('turma')
    turno = request.args.get('turno')
    
    # Filtrar alunos
    alunos = listar_alunos(turma, turno, ativo=True)
    
    return render_template('imprimir_qrcodes.html',
                           alunos=alunos,
                           turma=turma,
                           turno=turno,
                           turmas=TURMAS,
                           turnos=TURNOS,
                           hoje=date.today().strftime('%d/%m/%Y'))

@app.route('/backup')
def backup_database():
    """Faz download do banco de dados SQLite."""
    from config import DATABASE_PATH
    
    if not DATABASE_PATH.exists():
        flash('Banco de dados não encontrado.', 'danger')
        return redirect(url_for('dashboard'))
    
    return send_file(
        DATABASE_PATH,
        as_attachment=True,
        download_name=f'cantina_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
        mimetype='application/vnd.sqlite3'
    )

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f'404 - {request.path} - {request.remote_addr}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f'500 - {request.path} - {request.remote_addr} - {e}')
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f'Exceção não tratada: {e}')
    return render_template('500.html'), 500

# ========== LOGGING DE REQUESTS ==========
@app.before_request
def before_request():
    logger.info(f'Request: {request.method} {request.path} - {request.remote_addr}')

@app.after_request
def after_request(response):
    logger.info(f'Response: {request.method} {request.path} - {response.status_code}')
    return response

if __name__ == '__main__':
    import os
    # FIX: HTTPS necessário para câmera funcionar em rede local
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            ssl_context='adhoc',   # certificado autoassinado
            use_reloader=False     # evita duplicação do scheduler
        )
    except ImportError:
        print("⚠️  Para HTTPS, instale: pip install pyopenssl")
        print("   Rodando sem HTTPS (câmera só funciona em localhost)")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )