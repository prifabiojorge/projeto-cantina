"""
Módulo para envio de mensagens WhatsApp usando pywhatkit.
Funciona apenas se o WhatsApp Web já estiver logado no navegador padrão.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

from config import (
    WHATSAPP_ENABLED,
    WHATSAPP_PHONE_NUMBER,
    WHATSAPP_WAIT_TIME,
    WHATSAPP_CLOSE_TIME,
    REPORT_ADMIN_PHONE
)

logger = logging.getLogger(__name__)

def enviar_whatsapp(destinatario, mensagem):
    """
    Envia uma mensagem WhatsApp para o número especificado.
    
    Args:
        destinatario (str): Número no formato internacional (ex: +5511999999999)
        mensagem (str): Texto da mensagem
        
    Returns:
        bool: True se enviado com sucesso (ou simulado), False se erro.
    """
    if not WHATSAPP_ENABLED:
        logger.info(f'WhatsApp desabilitado. Mensagem simulada para {destinatario}: {mensagem}')
        print(f'[WhatsApp Simulado] Para {destinatario}: {mensagem}')
        return True
    
    if not destinatario or not destinatario.startswith('+'):
        logger.error(f'Número de destino inválido: {destinatario}')
        return False
    
    try:
        import pywhatkit as kit
        # pywhatkit.sendwhatmsg_instantly não existe; usamos sendwhatmsg com hora atual + 1 minuto
        # Mas há sendwhatmsg_instantly no pywhatkit 5.4? Vamos usar sendwhatmsg com hora atual.
        agora = datetime.now()
        kit.sendwhatmsg(
            phone_no=destinatario,
            message=mensagem,
            time_hour=agora.hour,
            time_min=agora.minute + 1,  # enviar daqui a 1 minuto
            wait_time=WHATSAPP_WAIT_TIME,
            tab_close=WHATSAPP_CLOSE_TIME,
            close_time=WHATSAPP_CLOSE_TIME
        )
        logger.info(f'Mensagem WhatsApp enviada para {destinatario}')
        return True
    except Exception as e:
        logger.error(f'Erro ao enviar WhatsApp para {destinatario}: {e}')
        return False

def enviar_relatorio_diario(total_esperado, total_real=None, detalhes=None):
    """
    Envia o relatório diário de previsão de almoços.
    
    Args:
        total_esperado (int): Total de alunos que fizeram check-in na portaria.
        total_real (int, optional): Total de alunos que já almoçaram (para relatório da cantina).
        detalhes (str, optional): Detalhamento por turma/turno.
        
    Returns:
        bool: Sucesso do envio.
    """
    from datetime import date
    hoje = date.today().strftime('%d/%m/%Y')
    
    if total_real is None:
        mensagem = f'''*Relatório Cantina Escola* - {hoje}

✅ *Previsão de almoços:* {total_esperado} alunos

Estes são os alunos que passaram pela portaria e devem receber almoço hoje.

_Enviado automaticamente pelo Sistema da Cantina_'''
    else:
        mensagem = f'''*Relatório Cantina Escola* - {hoje}

✅ *Previsão de almoços:* {total_esperado} alunos
🍽️ *Almoços servidos:* {total_real} alunos
📊 *Diferença:* {total_esperado - total_real} alunos

_Enviado automaticamente pelo Sistema da Cantina_'''
    
    if detalhes:
        mensagem += f'\n\n📋 Detalhes:\n{detalhes}'
    
    # Envia para o número configurado
    if REPORT_ADMIN_PHONE:
        return enviar_whatsapp(REPORT_ADMIN_PHONE, mensagem)
    else:
        logger.warning('Número de administrador não configurado. Relatório não enviado.')
        return False