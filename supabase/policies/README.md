# Policies Supabase

As policies principais estão em `supabase/migrations/202605180001_cantina_v2.sql`.

Papéis previstos:

- `admin`: acesso administrativo total.
- `portaria`: leitura de alunos e registro de check-in de portaria.
- `cantina`: leitura de alunos, leitura de portaria/cantina necessária ao fluxo e registro de almoço/liberação.

Os perfis são vinculados a `auth.users` pela tabela `perfis_usuarios`.
