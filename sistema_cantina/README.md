# Sistema Cantina Escolar

Sistema de controle de acesso e gestão de cantina escolar com QR codes, relatórios automatizados e painel administrativo.

## 🚀 Funcionalidades Principais

### 1. **Controle de Acesso com QR Codes**
- Cadastro de alunos com geração automática de QR code único
- Leitura de QR codes na portaria e cantina via webcam
- Interface otimizada para tablets e dispositivos móveis
- Sons e alertas visuais para confirmação de leitura

### 2. **Dashboard em Tempo Real**
- Visão geral do dia atual: alunos esperados, presentes, almoçaram
- Gráficos de histórico dos últimos 7 dias
- Alertas de alunos que não passaram pela portaria
- Filtros por turma, turno e data

### 3. **Relatórios Automatizados**
- Relatório diário por aluno (presença/almoco)
- Relatório por período (CSV e PDF)
- Envio automático via WhatsApp (configurável)
- Exportação de dados em CSV e PDF

### 4. **Gestão Administrativa**
- Cadastro, edição e desativação de alunos
- Impressão em lote de QR codes (layout otimizado para A4)
- Configurações do sistema via interface web
- Sistema de backup do banco de dados

### 5. **Recursos Técnicos**
- Banco de dados SQLite local
- Autenticação básica (senha configurável)
- Interface responsiva (Bootstrap 5)
- API REST para integrações futuras

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Webcam para leitura de QR codes (opcional)
- Navegador moderno (Chrome, Edge, Firefox)

## 🛠️ Instalação Rápida

### Opção 1: Usando o script de inicialização (Recomendado)

```bash
# Clone o repositório (se aplicável)
# cd sistema_cantina

# Execute o script de inicialização
python run.py
```

O script `run.py` irá:
1. Verificar dependências Python
2. Instalar pacotes faltantes automaticamente
3. Executar o seed inicial (60 alunos de teste)
4. Iniciar o servidor Flask em `http://0.0.0.0:5000`

### Opção 2: Instalação manual

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv

# 2. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar seed inicial (opcional)
python seed.py

# 5. Iniciar servidor
python app.py
```

## 🚀 Uso do Sistema

### Acesso Inicial
1. Acesse `http://localhost:5000` (ou IP do servidor)
2. Use as credenciais padrão (se configuradas)

### Fluxo de Trabalho

#### **Portaria**
- Acesse `/portaria`
- Autorize o acesso da câmera
- Aponte o QR code do aluno para a câmera
- O sistema registrará a entrada com som de confirmação

#### **Cantina**
- Acesse `/cantina`
- Leia o QR code dos alunos que vão almoçar
- O sistema controlará quem já passou pela portaria
- Alerta sonoro/visual para alunos não autorizados

#### **Administração**
- **Dashboard**: `/dashboard` - Visão geral do sistema
- **Alunos**: `/alunos` - Lista e cadastro de alunos
- **Relatórios**: `/relatorios` - Relatórios diários e por período
- **Configurações**: `/configuracoes` - Configurações do sistema
- **Backup**: `/backup` - Download do banco de dados

## 📊 Estrutura de Dados

### Tabelas Principais
- **alunos**: Dados dos alunos (nome, matrícula, turma, turno, QR code)
- **checkin_portaria**: Registro de entrada na escola
- **checkin_cantina**: Registro de almoço na cantina
- **relatorios_enviados**: Histórico de relatórios enviados
- **configuracoes**: Configurações do sistema

### Modelo de Dados
```sql
-- Aluno exemplo
{
  "id": 1,
  "nome": "Maria Silva",
  "matricula": "250327001",
  "turma": "8A",
  "turno": "manhã",
  "qrcode_hash": "abc123...",
  "ativo": true,
  "data_cadastro": "2025-03-27"
}
```

## ⚙️ Configuração

### Arquivo `config_escola.json`
```json
{
  "escola_nome": "Escola Municipal Exemplo",
  "whatsapp_enabled": false,
  "whatsapp_phone": "+5511999999999",
  "whatsapp_send_hour": 8,
  "whatsapp_send_minute": 0,
  "alarme_som": true,
  "alarme_visual": true,
  "dias_historico": 7
}
```

### Configurações via Interface
Acesse `/configuracoes` para ajustar:
- Nome da escola
- Envio automático de WhatsApp
- Horário de envio de relatórios
- Alertas sonoros/visuais
- Dias de histórico no dashboard

## 🧪 Dados de Teste

O sistema inclui um script `seed.py` para testes:

```bash
# Executar seed completo
python seed.py

# O script irá:
# 1. Criar 60 alunos brasileiros realistas
# 2. Gerar QR codes automaticamente
# 3. Simular check-ins dos últimos 30 dias
# 4. Simular relatórios enviados dos últimos 7 dias
```

### Opções do Seed
- `python seed.py` - Executa seed mantendo dados existentes
- Resposta `s` à pergunta de limpar dados - Remove todos os dados antes do seed

## 📁 Estrutura de Arquivos

```
sistema_cantina/
├── app.py                 # Aplicação Flask principal
├── config.py             # Configurações do sistema
├── database.py           # Configuração do banco de dados
├── models.py             # Modelos de dados e lógica de negócio
├── settings.py           # Gerenciamento de configurações JSON
├── seed.py               # População de dados de teste
├── run.py                # Script de inicialização automática
├── requirements.txt      # Dependências Python
├── config_escola.json    # Configurações da escola (JSON)
├── qrcodes_alunos/       # QR codes gerados (PNG)
├── static/
│   ├── css/              # Estilos CSS
│   ├── js/               # JavaScript
│   └── sounds/           # Sons do sistema
└── templates/
    ├── base.html         # Layout base
    ├── dashboard.html    # Dashboard
    ├── portaria.html     # Interface da portaria
    ├── cantina.html     # Interface da cantina
    ├── lista_alunos.html # Lista de alunos
    ├── configuracoes.html # Configurações
    └── ...               # Demais templates
```

## 🔧 Manutenção

### Backup do Banco de Dados
- Acesse `/backup` para download do arquivo `cantina.db`
- Ou copie manualmente `cantina.db`

### Logs do Sistema
- Os logs são exibidos no terminal onde o Flask está rodando
- Para produção, configure logging no arquivo `app.py`

### Atualização
1. Faça backup do banco de dados
2. Atualize o código
3. Verifique se há novas dependências em `requirements.txt`
4. Execute `pip install -r requirements.txt`
5. Reinicie o servidor

## 🌐 Implantação em Rede

### Para acesso em múltiplos dispositivos:

```bash
# Execute com host 0.0.0.0
python run.py
# ou
python app.py --host 0.0.0.0 --port 5000
```

### Configurações de Rede
- **IP do servidor**: Use `ipconfig` (Windows) ou `ifconfig` (Linux/Mac) para obter o IP
- **Acesso externo**: Configure firewall para permitir porta 5000
- **Dispositivos móveis**: Acesse `http://IP_DO_SERVIDOR:5000`

## 🚨 Solução de Problemas

### Problema: Câmera não funciona
- Verifique permissões do navegador
- Teste em `https://localhost:5000` (HTTPS local)
- Use navegadores Chrome/Edge

### Problema: QR code não é lido
- Verifique iluminação do ambiente
- Aproxime/suave o QR code da câmera
- Teste com QR codes impressos

### Problema: Banco de dados corrompido
- Restaure do backup (`/backup`)
- Ou execute `seed.py` para dados de teste

### Problema: Dependências faltando
```bash
pip install -r requirements.txt
```

## 📞 Suporte

### FAQ

**P: Posso usar o sistema sem webcam?**  
R: Sim, mas a leitura de QR codes será manual. Use a função de busca por matrícula.

**P: Quantos alunos o sistema suporta?**  
R: Testado com 200+ alunos. Performance pode variar com hardware.

**P: Posso personalizar os relatórios?**  
R: Sim, edite os templates em `templates/relatorio_*.html`

**P: O sistema funciona offline?**  
R: Sim, após instalado, funciona completamente offline.

**P: Posso migrar para outro banco de dados?**  
R: Sim, altere a configuração em `database.py` (suporte a PostgreSQL/MySQL).

### Recursos Adicionais
- [Documentação Flask](https://flask.palletsprojects.com/)
- [Gerador de QR codes Python](https://github.com/lincolnloop/python-qrcode)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/getting-started/introduction/)

## 📄 Licença

Este projeto é destinado a uso educacional e institucional. Consulte os autores para uso comercial.

## 👥 Autores

- Sistema desenvolvido para gestão escolar com foco em usabilidade e eficiência.

---

**Versão**: 2.0  
**Última atualização**: Março 2025  
**Próximas melhorias**: App móvel, sincronização em nuvem, relatórios avançados