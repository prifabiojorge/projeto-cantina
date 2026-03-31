import sqlite3
from pathlib import Path
from config import DATABASE_PATH

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('PRAGMA journal_mode = WAL')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            turma TEXT NOT NULL,
            turno TEXT NOT NULL,
            qrcode_hash TEXT UNIQUE NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_portaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            data DATE NOT NULL,
            hora_checkin DATETIME NOT NULL,
            UNIQUE(aluno_id, data),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_cantina (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            data DATE NOT NULL,
            hora_almoco DATETIME NOT NULL,
            UNIQUE(aluno_id, data),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relatorios_enviados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE UNIQUE NOT NULL,
            total_esperado INTEGER NOT NULL,
            enviado_em DATETIME NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT,
            descricao TEXT,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir configurações padrão se a tabela estiver vazia
    cursor.execute('SELECT COUNT(*) FROM configuracoes')
    if cursor.fetchone()[0] == 0:
        configuracoes_padrao = [
            ('escola_nome', 'Escola Municipal', 'Nome da escola'),
            ('whatsapp_enabled', 'false', 'Habilitar envio automático de relatório via WhatsApp'),
            ('whatsapp_phone', '', 'Número de telefone para envio do relatório (ex: +5511999999999)'),
            ('whatsapp_send_hour', '8', 'Hora do envio automático (0-23)'),
            ('whatsapp_send_minute', '0', 'Minuto do envio automático (0-59)'),
            ('alarme_som', 'true', 'Habilitar som de alarme na cantina'),
            ('alarme_visual', 'true', 'Habilitar alerta visual na cantina'),
            ('dias_historico', '7', 'Número de dias exibidos no histórico do dashboard')
        ]
        cursor.executemany(
            'INSERT INTO configuracoes (chave, valor, descricao) VALUES (?, ?, ?)',
            configuracoes_padrao
        )
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Banco de dados inicializado com sucesso.')