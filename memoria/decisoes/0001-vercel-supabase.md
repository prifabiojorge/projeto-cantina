# ADR 0001 - Vercel e Supabase na v2.0

## Decisão

A v2.0 usará Vercel como plataforma de deploy HTTPS e Supabase como banco
principal, autenticação e storage.

## Motivo

O sistema atual funciona bem em rede local, mas depende de um notebook servidor,
certificado autoassinado e SQLite local. Vercel e Supabase reduzem atrito de
acesso por smartphone, habilitam backup online, autenticação centralizada e
políticas de acesso por papel.

## Consequências

- SQLite fica como legado, contingência local e origem de migração.
- O deploy cloud não deve depender de arquivos escritos no filesystem local.
- APScheduler local será substituído por Vercel Cron em produção.
- Segredos reais devem existir apenas em variáveis de ambiente.
