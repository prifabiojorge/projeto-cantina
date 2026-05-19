# Evidencia de testes - v2.0 foundation

Data: 2026-05-18

## Comandos executados

- `python -m compileall api scripts sistema_cantina`
- `python test_routes.py`
- `python test_integration.py`
- `python test_dashboard.py`
- `python test_prompt6_routes.py`
- Simulacao Vercel: importacao de `api.index`, `GET /health` e cron protegido por `CRON_SECRET`.

## Resultado

- Compilacao Python concluida sem erros.
- Rotas legadas e rotas v2 carregadas com sucesso.
- Testes de dashboard e relatorios passaram.
- Testes de configuracoes, QR codes e backup passaram.
- Teste funcional de liberacao forcada passou, incluindo registro na cantina e presenca no relatorio diario.
- Teste funcional de importacao CSV pela interface administrativa passou.
- Teste funcional de exportacao JSON de configuracoes passou sem expor `callmebot_apikey`.
- Arquivo versionado `sistema_cantina/config_escola.json` foi saneado para nao guardar a chave CallMeBot.
- `GET /health` retornou HTTP 200.
- `GET /api/cron/relatorio-diario` retornou HTTP 401 sem segredo ou com segredo incorreto.
- Em modo Vercel, `/dashboard` anonimo redirecionou para login e perfil `cantina` recebeu HTTP 403.
- Dependencias de `requirements.txt` instaladas com sucesso no ambiente Python 3.12.
- `pip check` executado sem conflitos.
- Migracao SQLite -> Supabase executada com sucesso: 425 alunos, 1613 check-ins de portaria, 1485 check-ins de cantina e 8 configuracoes confirmadas no Supabase.

## Observacoes

- Testes locais foram executados com `CANTINA_DISABLE_SCHEDULER=true` para evitar execucao do agendador legado.
- Supabase nao foi chamado de verdade porque as variaveis reais do projeto ainda nao estao configuradas neste ambiente.
