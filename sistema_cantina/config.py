import os
from pathlib import Path
import settings

BASE_DIR = Path(__file__).parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

DATABASE_PATH = BASE_DIR / 'cantina.db'

QRCODE_DIR = BASE_DIR / 'qrcodes_alunos'
QRCODE_DIR.mkdir(exist_ok=True)

# Configurações da escola (carregadas do JSON via settings.py)
TURMAS = settings.TURMAS
TURNOS = settings.TURNOS
ESCOLA_NOME = settings.ESCOLA_NOME

# Configurações WhatsApp (combinadas com variáveis de ambiente)
WHATSAPP_ENABLED = os.environ.get('WHATSAPP_ENABLED', str(settings.WHATSAPP_HABILITADO)).lower() == 'true'
WHATSAPP_PHONE_NUMBER = os.environ.get('WHATSAPP_PHONE_NUMBER', settings.WHATSAPP_NUMERO)
WHATSAPP_GRUPO_ID = settings.WHATSAPP_GRUPO_ID
WHATSAPP_METODO = settings.WHATSAPP_METODO

# Extrair hora e minuto do horário de envio
try:
    hora_str = settings.WHATSAPP_HORARIO
    if ':' in hora_str:
        h, m = hora_str.split(':')
        WHATSAPP_SEND_HOUR = int(h)
        WHATSAPP_SEND_MINUTE = int(m)
    else:
        WHATSAPP_SEND_HOUR = 8
        WHATSAPP_SEND_MINUTE = 0
except (ValueError, AttributeError):
    WHATSAPP_SEND_HOUR = 8
    WHATSAPP_SEND_MINUTE = 0

WHATSAPP_WAIT_TIME = 15  # Tempo de espera para envio (segundos)
WHATSAPP_CLOSE_TIME = 2  # Tempo para fechar a guia (segundos)

# Configurações do relatório
REPORT_ADMIN_PHONE = os.environ.get('REPORT_ADMIN_PHONE', WHATSAPP_PHONE_NUMBER)