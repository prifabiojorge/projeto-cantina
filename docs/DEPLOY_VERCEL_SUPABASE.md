# Deploy Vercel + Supabase

Este guia segue o mesmo padrão do Projeto Vinicius, adaptado para Flask.

## 1. Supabase

1. Crie um projeto Supabase.
2. Habilite login por email/senha em Authentication.
3. Execute `supabase/migrations/202605180001_cantina_v2.sql`.
4. Em Project Settings > API, copie:
   - Project URL;
   - anon public key;
   - service role key.

## 2. Ambiente

Copie `.env.example` para `.env` e preencha os valores reais. Não versionar
`.env`.

## 3. Vercel

1. Conecte o repositório ao GitHub.
2. Crie um projeto Vercel na raiz do repositório.
3. Cadastre as variáveis de ambiente do `.env.example`.
   - Em produção, use `V2_AUTH_REQUIRED=true`.
   - Use `CANTINA_DISABLE_SCHEDULER=true`; o agendamento fica no Vercel Cron.
   - Use `FLASK_DEBUG=false`.
   - Configure `CALLMEBOT_API_KEY` apenas como variável de ambiente.
   - Use `WHATSAPP_ENABLED=true` somente depois de validar `WHATSAPP_PHONE_NUMBER` e `CALLMEBOT_API_KEY`.
4. Faça deploy.

## 4. Validação

- `/health` retorna status da aplicação.
- `/login` autentica usuário administrativo.
- `/portaria` e `/cantina` abrem em HTTPS.
- `/api/cron/relatorio-diario` responde apenas com `CRON_SECRET`.
- `/alunos/importar` importa CSV administrativo.
- `/configuracoes/exportar` exporta JSON sem segredos.
