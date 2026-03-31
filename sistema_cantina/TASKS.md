# Arquivo de Tasks — Correções Realizadas

## Problema 1: Comando sqlite3 não funciona no Windows

**Solução:** Script Python para executar consultas SQL.

**Arquivo:** `consultar_db.py`

**Uso:**
```bash
# Consulta única
python consultar_db.py "SELECT * FROM alunos LIMIT 5"

# Modo interativo
python consultar_db.py

# Dentro do modo interativo:
SQL> SELECT id, nome FROM alunos WHERE nome LIKE '%Emanuelly%'
SQL> tabelas  # lista todas as tabelas
SQL> sair     # encerra
```

**Status:** ✅ RESOLVIDO

---

## Problema 2: Scanner muito pequeno (retângulo comprido e curto)

**Alterações realizadas:**

1. **cantina.html** — CSS:
   - `#reader { height: 500px; }` (era 400px)

2. **cantina.html** — JavaScript:
   - `qrbox: { width: 300, height: 300 }` (era 250x250)

3. **portaria.html** — CSS:
   - `#reader { height: 500px; }` (era 400px)

4. **portaria.html** — JavaScript:
   - `qrbox: { width: 300, height: 300 }` (era 250x250)

**Status:** ✅ RESOLVIDO

---

## Problema 3: Teste com aluno Emanuelly Teixeira

**Registros limpos:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('cantina.db'); cursor = conn.cursor(); cursor.execute(\"DELETE FROM checkin_portaria WHERE aluno_id = 1 AND data = date('now')\"); cursor.execute(\"DELETE FROM checkin_cantina WHERE aluno_id = 1 AND data = date('now')\"); conn.commit(); conn.close()"
```

**Status:** ✅ RESOLVIDO

---

## Arquivos Criados/Modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `consultar_db.py` | CRIADO | Script para consultas SQL sem sqlite3 |
| `templates/cantina.html` | MODIFICADO | Scanner maior (500px) e qrbox 300x300 |
| `templates/portaria.html` | MODIFICADO | Scanner maior (500px) e qrbox 300x300 |
| `TASKS.md` | ATUALIZADO | Status das correções |

---

## Próximos Passos para o Usuário

1. **Recarregar a página no navegador** (F5) para ver as alterações
2. **Testar o scanner** com o QR code do aluno Emanuelly
3. **Verificar se o tamanho está adequado**
4. **Testar check-in na portaria e cantina**

---

## Comandos Úteis

```bash
# Consultar aluno
python consultar_db.py "SELECT id, nome, matricula FROM alunos WHERE nome LIKE '%Emanuelly%'"

# Verificar check-ins de hoje
python consultar_db.py "SELECT * FROM checkin_portaria WHERE data = date('now')"

# Verificar almoços de hoje
python consultar_db.py "SELECT * FROM checkin_cantina WHERE data = date('now')"

# Limpar registros de um aluno (substitua 1 pelo ID correto)
python -c "import sqlite3; conn = sqlite3.connect('cantina.db'); cursor = conn.cursor(); cursor.execute(\"DELETE FROM checkin_portaria WHERE aluno_id = 1 AND data = date('now')\"); cursor.execute(\"DELETE FROM checkin_cantina WHERE aluno_id = 1 AND data = date('now')\"); conn.commit(); print('Limpo'); conn.close()"
```

---

*Atualizado em 27/03/2026*
