# Plano v2.0 - Vercel + Supabase

## Objetivo

Evoluir o Sistema Cantina Escolar para uma versão cloud-first com Vercel para
HTTPS/deploy e Supabase para Postgres, Auth, Storage e políticas de acesso.

## Padrão adotado do Projeto Vinicius

- `.env.example` sem segredos reais.
- Supabase configurado por variáveis de ambiente.
- Migrations SQL versionadas em `supabase/migrations/`.
- Vercel documentado com deploy por GitHub e variáveis de ambiente.
- `memoria/` na raiz do projeto para registrar decisões e contexto.

## Etapas

1. Preparar memória, env, Vercel e migrations Supabase.
2. Criar camada Python de Supabase com fallback local seguro.
3. Migrar dados do SQLite atual para Supabase por script.
4. Proteger área administrativa com Supabase Auth.
5. Levar relatório diário para Vercel Cron.
6. Mover QR codes, PDFs e backups para Supabase Storage.
7. Validar fluxo completo em smartphone e desktop.
