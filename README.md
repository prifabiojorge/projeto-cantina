# Sistema Cantina Escolar

Aplicação de controle de refeições da **Escola Estadual Celso Rodrigues**, uma escola de tempo integral. O sistema usa QR Codes para registrar a passagem dos alunos pela portaria e a entrega de refeições na cantina.

A versão 2 utiliza **Flask**, hospedagem na **Vercel** e **Supabase** para autenticação e persistência dos dados. O SQLite continua disponível para execução local legada.

## Acesso ao aplicativo

- [Entrar no sistema](https://projeto-cantina-nine.vercel.app/login)
- [Administração](https://projeto-cantina-nine.vercel.app/dashboard)
- [Portaria](https://projeto-cantina-nine.vercel.app/portaria)
- [Cantina](https://projeto-cantina-nine.vercel.app/cantina)

Esses endereços abrem o aplicativo. Os painéis da Vercel e do Supabase são usados na configuração e manutenção; não precisam permanecer abertos durante o atendimento.

## Como funciona

1. A administração cadastra ou importa os alunos e disponibiliza seus QR Codes.
2. Na portaria, a leitura do QR Code registra a previsão de almoço daquele dia.
3. Na cantina, a leitura verifica se o aluno está ativo, passou pela portaria e ainda não recebeu a refeição.
4. A entrega é registrada. Uma segunda tentativa de almoço no mesmo dia é bloqueada.
5. A administração acompanha as contagens, o histórico e os relatórios.

Quando necessária, a liberação forçada registra a refeição com motivo e responsável. No Supabase, essa operação depende da migração SQL específica para gravar a refeição e a justificativa na mesma transação.

O cadastro assume `Integral`. Esse valor permanece no banco por compatibilidade; algumas telas e exportações legadas ainda exibem referências a Turno.

## Perfis de acesso

| Perfil | Uso |
| --- | --- |
| `admin` | Alunos, dashboard, relatórios, configurações, backup e estações de operação. |
| `portaria` | Estação e registros da portaria. |
| `cantina` | Estação e registros da cantina. |

Em produção, as estações também exigem login. Use contas individuais e navegadores ou perfis de navegador distintos para manter sessões independentes. Janelas do mesmo perfil compartilham a sessão.

A câmera deve ser autorizada no navegador. Para acesso pela rede, utilize HTTPS; no desenvolvimento, `localhost` permite testar a câmera em navegadores compatíveis.

## Recursos disponíveis

- Cadastro, edição, ativação e desativação de alunos.
- Importação administrativa por CSV com `nome` e `matricula`; a coluna `turma` também pode ser informada.
- QR Codes individuais e impressão em lote.
- Check-ins de portaria e cantina, com controle de duplicidade.
- Liberação forçada com justificativa.
- Dashboard, histórico, relatórios diários e exportações CSV/PDF.
- Configurações e exportação de configurações.
- Backup lógico JSON no modo Supabase; download do banco no modo SQLite.
- Integração opcional com WhatsApp e endpoint de agendamento diário.

## Organização do repositório

```text
api/index.py                 Entrada da aplicação na Vercel
sistema_cantina/
  app.py                     Rotas e páginas existentes
  models.py                  Interface de dados e implementação SQLite
  cloud_models.py            Operações e consultas Supabase
  app/                       Inicialização, autenticação e camadas da v2
  templates/                 Páginas HTML
  static/                    Arquivos estáticos
scripts/                     Migração, administração e verificações
supabase/migrations/         Estrutura do banco, políticas e funções SQL
docs/                        Guias complementares
memoria/                     Decisões, contexto, planos e evidências
vercel.json                  Roteamento e agendamento de produção
requirements.txt             Dependências Python
```

As rotas existentes continuam em `sistema_cantina/app.py`. O pacote `app/` instala autenticação e integrações sobre essa aplicação. Em Vercel, `models.py` utiliza `cloud_models.py`; uma falha de conexão não provoca retorno automático ao SQLite.

## Instalação para desenvolvimento

Use Python 3.12 e um ambiente virtual. No PowerShell, a partir da raiz do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha o `.env` com as credenciais do seu ambiente. Para iniciar localmente usando o Supabase:

```powershell
$env:CANTINA_DATA_BACKEND = 'supabase'
$env:V2_AUTH_REQUIRED = 'true'
$env:CANTINA_DISABLE_SCHEDULER = 'true'
.\.venv\Scripts\python.exe -m flask --app api.index:app run --host 127.0.0.1 --port 5000
```

Abra [http://localhost:5000/login](http://localhost:5000/login). O Flask carrega o `.env` por meio de `python-dotenv`. O servidor de desenvolvimento deve ser usado apenas para desenvolvimento.

Para trabalhar com o SQLite local, remova `CANTINA_DATA_BACKEND` do ambiente antes de iniciar. Os dados locais e remotos são independentes: não há sincronização automática nem modo offline sincronizado.

## Preparação do Supabase

Em um projeto novo:

1. Execute no SQL Editor as migrações de `supabase/migrations/`, na ordem dos nomes dos arquivos.
2. Habilite autenticação por e-mail e senha e crie as contas em Authentication.
3. Crie o perfil de cada conta em `perfis_usuarios`, vinculando o `user_id` ao usuário de Authentication, com `papel` e `ativo=true`.
4. Configure as credenciais do projeto no ambiente da aplicação.

O script `scripts/criar_admin.py` auxilia na criação do perfil. Ele não cria a conta nem define sua senha. Recebe `AUTH_USER_ID`, `AUTH_USER_NAME` e `AUTH_USER_ROLE` pelo ambiente.

As tabelas têm políticas de Row Level Security. As operações atuais do servidor utilizam a chave `service_role`, que contorna essas políticas; por isso, as verificações de perfil nas rotas Flask também são necessárias. Essa chave nunca deve ser enviada ao navegador.

Os buckets `qrcodes`, `relatorios` e `backups` são preparados pela migração inicial. Atualmente os downloads principais são gerados em memória; a existência dos buckets não significa que todos os arquivos sejam armazenados neles.

## Variáveis de ambiente

| Variável | Finalidade |
| --- | --- |
| `SUPABASE_URL` | Endereço do projeto Supabase. |
| `SUPABASE_ANON_KEY` | Chave usada pelo cliente de autenticação. |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave privilegiada, exclusiva do servidor. |
| `SECRET_KEY` | Segredo forte e aleatório para assinar as sessões Flask. |
| `V2_AUTH_REQUIRED` | Use `true` em produção. |
| `CANTINA_DATA_BACKEND` | Use `supabase` para testar o banco remoto localmente; na Vercel essa seleção é automática. |
| `CANTINA_DISABLE_SCHEDULER` | Use `true` na Vercel; o agendamento é externo. |
| `CRON_SECRET` | Segredo que autoriza a chamada do relatório agendado. |
| `FLASK_DEBUG` | Use `false` em produção. |
| `WHATSAPP_ENABLED` | Mantenha `false` até validar a integração. |
| `WHATSAPP_PHONE_NUMBER` | Destinatário das mensagens, quando habilitadas. |
| `CALLMEBOT_API_KEY` | Credencial da integração CallMeBot. |

`SUPABASE_JWT_SECRET` está presente na configuração legada da v2, mas o login atual usa Supabase Auth e não valida JWT localmente com esse segredo.

## Publicação na Vercel

1. Importe o repositório na Vercel usando a raiz como diretório do projeto.
2. Configure as variáveis do ambiente de produção, sobretudo autenticação, chaves Supabase e `SECRET_KEY`.
3. Aplique as migrações necessárias no Supabase antes de publicar funcionalidades que dependam delas.
4. Envie o código à branch conectada ao deploy e aguarde o status **Ready**.
5. Confira `/health`, faça login e valide a lista de alunos e as permissões.

Alterações de variáveis precisam de um novo deploy para entrar em vigor. A Vercel hospeda o código; os registros persistentes ficam no Supabase.

O `vercel.json` configura o relatório diário para **11:00 UTC**, equivalente a **08:00 em Fortaleza**. A rota `/api/cron/relatorio-diario` exige `CRON_SECRET`; para chamadas manuais, utilize o cabeçalho `Authorization: Bearer <CRON_SECRET>`. O envio ao WhatsApp ainda depende da configuração e validação da integração.

Consulte também o [guia de deploy](docs/DEPLOY_VERCEL_SUPABASE.md).

## Verificação e testes

Em modo Supabase, `/health` deve retornar `backend: "supabase"`, `database: true` e `status: "ok"`. Isso confirma uma consulta básica ao banco; não substitui o teste do fluxo completo.

Com um ambiente separado para testes, execute:

```powershell
.\.venv\Scripts\python.exe scripts/testar_corte_supabase.py
```

O teste consulta as telas, cria um aluno temporário, verifica QR Code, portaria, cantina, duplicidade e permissões, e remove o aluno criado ao final. Ele acessa o projeto informado no `.env` e realiza gravações reais. Não verifica câmera física, envio WhatsApp nem a transação SQL de liberação forçada.

## Dados reais e manutenção

Os alunos reais foram importados de uma lista privada. Como a fonte não continha matrículas oficiais, foram utilizados identificadores internos no formato `2026-TURMA-CHAMADA`. Os nomes e a lista nominal não devem ser publicados neste repositório.

Não execute seeds ou scripts de substituição para iniciar o aplicativo. `scripts/substituir_alunos_reais.py --executar` apaga cadastros e históricos antes de inserir a lista; seu uso é reservado a uma substituição expressamente autorizada e com backup. `scripts/migrar_sqlite_para_supabase.py` também é uma operação de migração, não de inicialização diária.

Mantenha `.env`, bancos, backups, QR Codes e listas nominais fora do Git. Se uma credencial for publicada, remova-a dos arquivos e rotacione-a no serviço de origem: a remoção não elimina cópias nem o histórico do Git.

Registre mudanças e evidências em [memoria/](memoria/README.md), sem incluir senhas, tokens ou dados pessoais completos.
