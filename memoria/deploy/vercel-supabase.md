# Deploy v2.0 - Vercel + Supabase

## Supabase

1. Criar projeto Supabase.
2. Em Authentication, habilitar email/senha.
3. Executar `supabase/migrations/202605180001_cantina_v2.sql` no SQL Editor.
4. Criar usuários no Auth e perfis em `perfis_usuarios`.
5. Copiar Project URL, anon key e service role key.

## Vercel

1. Conectar o repositório ao GitHub.
2. Criar projeto na Vercel apontando para a raiz do repositório.
3. Configurar variáveis do `.env.example`.
   - `V2_AUTH_REQUIRED=true`
   - `CANTINA_DISABLE_SCHEDULER=true`
   - `FLASK_DEBUG=false`
4. Fazer deploy.
5. Testar `/health`, `/login`, `/portaria`, `/cantina` e `/dashboard`.

## Cron

O cron em `vercel.json` roda às `11:00 UTC`, equivalente a `08:00` em
America/Fortaleza.
