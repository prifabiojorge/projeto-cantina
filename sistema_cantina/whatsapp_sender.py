"""
Módulo para envio de mensagens WhatsApp usando CallMeBot API.
Suporte também a pywhatkit como fallback.

CallMeBot: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""
import logging
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def _get_config():
    """Carrega configurações do arquivo JSON."""
    import json
    config_path = Path(__file__).parent / 'config_escola.json'
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
    try:
        # Codificar mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem)
        
        # Montar URL da API CallMeBot
        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={phone}"
            f"&text={mensagem_encoded}"
            f"&apikey={apikey}"
        )
        
        # Fazer requisição
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            resultado = response.read().decode('utf-8')
            
        if 'Message queued' in resultado or '200' in resultado:
            logger.info(f'Mensagem WhatsApp enviada com sucesso para {phone}')
            return True
        else:
            logger.warning(f'Resposta inesperada do CallMeBot: {resultado}')
            return False
            
    except urllib.error.URLError as e:
        logger.error(f'Erro de rede ao enviar WhatsApp: {e}')
        return False
    except Exception as e:
        logger.error(f'Erro ao enviar WhatsApp via CallMeBot: {e}')
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
    
    habilitado = whatsapp_config.get('habilitado', False)
    metodo = whatsapp_config.get('metodo', 'callmebot')
    phone = whatsapp_config.get('numero_telefone', '')
    apikey = whatsapp_config.get('callmebot_apikey', '')
    
    if not habilitado:
        logger.info('WhatsApp desabilitado. Mensagem simulada:')
        logger.info(f'  Para: {destinatario}')
        logger.info(f'  Texto: {mensagem[:100]}...')
        print(f'\n[WhatsApp Desabilitado] Mensagem simulada:')
        print(f'  Para: {destinatario}')
        print(f'  Texto: {mensagem[:200]}...' if len(mensagem) > 200 else f'  Texto: {mensagem}')
        return True
    
    # Tentar CallMeBot primeiro
    if metodo == 'callmebot' and phone and apikey:
        resultado = enviar_whatsapp_callmebot(phone, apikey, mensagem)
        if resultado:
            return True
        logger.warning('CallMeBot falhou, tentando pywhatkit como fallback...')
    
    # Fallback para pywhatkit
    if destinatario:
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
