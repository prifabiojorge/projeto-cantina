"""
Módulo para envio de mensagens WhatsApp usando CallMeBot API.
Suporte também a pywhatkit como fallback.

CallMeBot: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""
import logging
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def _get_config():
    """Carrega configurações do arquivo JSON."""
    import json
    config_path = Path(__file__).parent / 'config_escola.json'
    if not config_path.exists():
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('whatsapp', {})
    except Exception as e:
        logger.error(f'Erro ao carregar config: {e}')
        return {}


def enviar_whatsapp_callmebot(phone, apikey, mensagem):
    """
    Envia mensagem WhatsApp via CallMeBot API.
    
    Args:
        phone (str): Número no formato internacional sem + (ex: 559185140988)
        apikey (str): API key do CallMeBot
        mensagem (str): Texto da mensagem
        
    Returns:
        bool: True se enviado com sucesso, False se erro.
    """
    for tentativa in range(1, 4):
        try:
            url = 'https://api.callmebot.com/whatsapp.php?' + urllib.parse.urlencode(
                {'phone': phone, 'text': mensagem, 'apikey': apikey})
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # Three attempts plus backoff must fit the 60-second function limit.
            with urllib.request.urlopen(req, timeout=12) as response:
                resultado = response.read().decode('utf-8')

            if 'Message queued' in resultado:
                logger.info('Mensagem aceita na fila do CallMeBot.')
                return True

            logger.warning('CallMeBot nao confirmou envio na tentativa %s.', tentativa)
        except urllib.error.URLError as e:
            logger.error('Erro de rede no CallMeBot na tentativa %s (%s).', tentativa, type(e).__name__)
        except Exception as e:
            logger.error('Erro no CallMeBot na tentativa %s (%s).', tentativa, type(e).__name__)

        if tentativa < 3:
            time.sleep(2 ** (tentativa - 1))

    return False


def enviar_whatsapp_pywhatkit(destinatario, mensagem):
    """
    Envia mensagem WhatsApp via pywhatkit (fallback).
    Requer WhatsApp Web logado no navegador.
    """
    try:
        import pywhatkit as kit
        agora = datetime.now()
        kit.sendwhatmsg(
            phone_no=destinatario,
            message=mensagem,
            time_hour=agora.hour,
            time_min=agora.minute + 1,
            wait_time=15,
            tab_close=True,
            close_time=2
        )
        logger.info(f'Mensagem WhatsApp enviada via pywhatkit para {destinatario}')
        return True
    except Exception as e:
        logger.error(f'Erro ao enviar WhatsApp via pywhatkit: {e}')
        return False


def enviar_whatsapp(destinatario, mensagem):
    """
    Envia mensagem WhatsApp usando o método configurado.
    Prioridade: CallMeBot > pywhatkit.
    
    Args:
        destinatario (str): Número de telefone
        mensagem (str): Texto da mensagem
        
    Returns:
        bool: True se enviado com sucesso, False se erro.
    """
    whatsapp_config = _get_config()
    
    env_enabled = os.environ.get('WHATSAPP_ENABLED')
    habilitado = (
        env_enabled.strip().lower() in {'1', 'true', 'yes', 'on', 'sim'}
        if env_enabled is not None
        else whatsapp_config.get('habilitado', False)
    )
    metodo = os.environ.get('WHATSAPP_METHOD', '').strip() or whatsapp_config.get('metodo', 'callmebot')
    phone = os.environ.get('WHATSAPP_PHONE_NUMBER', '').strip() or whatsapp_config.get('numero_telefone', '')
    apikey = os.environ.get('CALLMEBOT_API_KEY', '').strip()
    
    if not habilitado:
        logger.info('WhatsApp desabilitado; nenhuma mensagem enviada.')
        return False
    
    # Tentar CallMeBot primeiro
    if metodo == 'callmebot' and phone and apikey:
        return enviar_whatsapp_callmebot(phone, apikey, mensagem)
    
    # Fallback para pywhatkit
    if destinatario and not os.environ.get('VERCEL'):
        return enviar_whatsapp_pywhatkit(destinatario, mensagem)
    
    logger.error('Nenhum método de envio WhatsApp configurado corretamente.')
    return False


def enviar_relatorio_diario(total_esperado, total_real=None, detalhes=None):
    """
    Envia o relatório diário de previsão de almoços.
    
    Args:
        total_esperado (int): Total de alunos que fizeram check-in na portaria.
        total_real (int, optional): Total de alunos que já almoçaram.
        detalhes (str, optional): Detalhamento por turma/turno.
        
    Returns:
        bool: Sucesso do envio.
    """
    from datetime import date
    hoje = date.today().strftime('%d/%m/%Y')
    
    if total_real is None:
        mensagem = f"""📋 *Relatório Cantina Escola* - {hoje}

✅ *Previsão de almoços:* {total_esperado} alunos

Estes são os alunos que passaram pela portaria e devem receber almoço hoje.

_Enviado automaticamente pelo Sistema da Cantina_"""
    else:
        mensagem = f"""📋 *Relatório Cantina Escola* - {hoje}

✅ *Previsão de almoços:* {total_esperado} alunos
🍽️ *Almoços servidos:* {total_real} alunos
📊 *Diferença:* {total_esperado - total_real} alunos

_Enviado automaticamente pelo Sistema da Cantina_"""
    
    if detalhes:
        mensagem += f'\n\n📋 *Detalhes:*\n{detalhes}'
    
    # Envia via CallMeBot (ou método configurado)
    return enviar_whatsapp('', mensagem)
