"""
Módulo de configurações do sistema Cantina Escolar.

Gerencia configurações em arquivo JSON (config_escola.json) e mantém compatibilidade
com a tabela 'configuracoes' do banco de dados existente.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sqlite3

BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'cantina.db'

# Caminho para o arquivo de configurações JSON
CONFIG_JSON_PATH = Path(__file__).parent / 'config_escola.json'

# Estrutura padrão das configurações
DEFAULT_CONFIG = {
    "escola": {
        "nome": "Escola Municipal",
        "turmas": ["1ºA", "1ºB", "2ºA", "2ºB", "3ºA", "3ºB"],
        "turnos": ["Manhã", "Tarde", "Integral"]
    },
    "whatsapp": {
        "habilitado": False,
        "horario_envio": "08:00",
        "grupo_id": "",
        "metodo": "pywhatkit",  # ou "api"
        "numero_telefone": ""
    },
    "sistema": {
        "alarme_som": True,
        "alarme_visual": True,
        "dias_historico": 7,
        "backup_automatico": False
    }
}

def load_settings():
    """Carrega as configurações do arquivo JSON. Cria o arquivo com padrão se não existir."""
    if not CONFIG_JSON_PATH.exists():
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Garantir que todas as seções padrão existam
        for section, default_values in DEFAULT_CONFIG.items():
            if section not in settings:
                settings[section] = default_values
            else:
                # Garantir que todas as chaves dentro da seção existam
                for key, value in default_values.items():
                    if key not in settings[section]:
                        settings[section][key] = value
        
        return settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Erro ao carregar configurações: {e}. Usando configurações padrão.")
        return DEFAULT_CONFIG.copy()

def save_settings(settings):
    """Salva as configurações no arquivo JSON."""
    try:
        with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        sync_to_database(settings)
        return True
    except IOError as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

def get_setting(section, key, default=None):
    """Obtém um valor de configuração específico."""
    settings = load_settings()
    return settings.get(section, {}).get(key, default)

def update_setting(section, key, value):
    """Atualiza um valor de configuração específico e salva no arquivo."""
    settings = load_settings()
    if section not in settings:
        settings[section] = {}
    settings[section][key] = value
    return save_settings(settings)

def sync_to_database(settings):
    """
    Sincroniza as configurações do JSON com a tabela 'configuracoes' do banco de dados
    para manter compatibilidade com código existente.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Mapeamento de configurações do JSON para chaves da tabela
        mapping = [
            ('escola_nome', settings['escola']['nome'], 'Nome da escola'),
            ('whatsapp_enabled', 'true' if settings['whatsapp']['habilitado'] else 'false', 'Habilitar envio automático de relatório via WhatsApp'),
            ('whatsapp_phone', settings['whatsapp']['numero_telefone'], 'Número de telefone para envio do relatório'),
            ('whatsapp_send_hour', settings['whatsapp']['horario_envio'].split(':')[0], 'Hora do envio automático (0-23)'),
            ('whatsapp_send_minute', settings['whatsapp']['horario_envio'].split(':')[1], 'Minuto do envio automático (0-59)'),
            ('whatsapp_grupo_id', settings['whatsapp']['grupo_id'], 'ID do grupo WhatsApp para envio de relatórios'),
            ('whatsapp_metodo', settings['whatsapp']['metodo'], 'Método de envio WhatsApp (pywhatkit ou api)'),
            ('alarme_som', 'true' if settings['sistema']['alarme_som'] else 'false', 'Habilitar som de alarme na cantina'),
            ('alarme_visual', 'true' if settings['sistema']['alarme_visual'] else 'false', 'Habilitar alerta visual na cantina'),
            ('dias_historico', str(settings['sistema']['dias_historico']), 'Número de dias exibidos no histórico do dashboard')
        ]
        
        for chave, valor, descricao in mapping:
            cursor.execute('''
                INSERT INTO configuracoes (chave, valor, descricao, atualizado_em)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(chave) DO UPDATE SET
                    valor = excluded.valor,
                    descricao = excluded.descricao,
                    atualizado_em = CURRENT_TIMESTAMP
            ''', (chave, valor, descricao))
        
        # Inserir turmas e turnos como configurações separadas
        turmas_str = '\n'.join(settings['escola']['turmas'])
        turnos_str = '\n'.join(settings['escola']['turnos'])
        
        cursor.execute('''
            INSERT INTO configuracoes (chave, valor, descricao, atualizado_em)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                descricao = excluded.descricao,
                atualizado_em = CURRENT_TIMESTAMP
        ''', ('turmas_disponiveis', turmas_str, 'Turmas disponíveis (uma por linha)'))
        
        cursor.execute('''
            INSERT INTO configuracoes (chave, valor, descricao, atualizado_em)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                descricao = excluded.descricao,
                atualizado_em = CURRENT_TIMESTAMP
        ''', ('turnos_disponiveis', turnos_str, 'Turnos disponíveis (uma por linha)'))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao sincronizar configurações com banco de dados: {e}")
        return False

def sync_from_database():
    """
    Sincroniza as configurações do banco de dados para o arquivo JSON.
    Útil para migração de configurações existentes.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT chave, valor FROM configuracoes')
        rows = cursor.fetchall()
        conn.close()
        
        settings = load_settings()
        
        for chave, valor in rows:
            if chave == 'escola_nome':
                settings['escola']['nome'] = valor
            elif chave == 'whatsapp_enabled':
                settings['whatsapp']['habilitado'] = valor.lower() == 'true'
            elif chave == 'whatsapp_phone':
                settings['whatsapp']['numero_telefone'] = valor
            elif chave == 'whatsapp_send_hour' and 'whatsapp_send_minute' in dict(rows):
                # Buscar minuto
                minuto = dict(rows).get('whatsapp_send_minute', '0')
                settings['whatsapp']['horario_envio'] = f"{valor.zfill(2)}:{minuto.zfill(2)}"
            elif chave == 'whatsapp_grupo_id':
                settings['whatsapp']['grupo_id'] = valor
            elif chave == 'whatsapp_metodo':
                settings['whatsapp']['metodo'] = valor if valor in ['pywhatkit', 'api'] else 'pywhatkit'
            elif chave == 'alarme_som':
                settings['sistema']['alarme_som'] = valor.lower() == 'true'
            elif chave == 'alarme_visual':
                settings['sistema']['alarme_visual'] = valor.lower() == 'true'
            elif chave == 'dias_historico':
                try:
                    settings['sistema']['dias_historico'] = int(valor)
                except ValueError:
                    pass
            elif chave == 'turmas_disponiveis':
                turmas = [t.strip() for t in valor.split('\n') if t.strip()]
                if turmas:
                    settings['escola']['turmas'] = turmas
            elif chave == 'turnos_disponiveis':
                turnos = [t.strip() for t in valor.split('\n') if t.strip()]
                if turnos:
                    settings['escola']['turnos'] = turnos
        
        save_settings(settings)
        return settings
    except sqlite3.Error as e:
        print(f"Erro ao sincronizar do banco de dados: {e}")
        return load_settings()

def migrate_from_database():
    """Migra todas as configurações do banco de dados para o arquivo JSON (executar uma vez)."""
    print("Migrando configurações do banco de dados para arquivo JSON...")
    settings = sync_from_database()
    print("Migração concluída.")
    return settings

# Inicialização: carregar configurações e sincronizar com banco se necessário
SETTINGS = load_settings()

# Atalhos para configurações comuns
ESCOLA_NOME = SETTINGS['escola']['nome']
TURMAS = SETTINGS['escola']['turmas']
TURNOS = SETTINGS['escola']['turnos']
WHATSAPP_HABILITADO = SETTINGS['whatsapp']['habilitado']
WHATSAPP_HORARIO = SETTINGS['whatsapp']['horario_envio']
WHATSAPP_GRUPO_ID = SETTINGS['whatsapp']['grupo_id']
WHATSAPP_METODO = SETTINGS['whatsapp']['metodo']
WHATSAPP_NUMERO = SETTINGS['whatsapp']['numero_telefone']