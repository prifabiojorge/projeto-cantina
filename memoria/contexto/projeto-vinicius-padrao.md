# Padrão observado no Projeto Vinicius

O Projeto Vinicius usa uma aplicação web deployada na Vercel e Supabase para
Auth/Postgres. Os pontos reaproveitados na Cantina v2 são:

- arquivo `.env.example` com placeholders;
- migrations SQL em `supabase/migrations`;
- RLS ativa nas tabelas;
- policies que isolam dados por usuário/papel;
- documentação de deploy em Vercel;
- pasta `memoria/` na raiz do repositório.

Na Cantina, a adaptação preserva Flask/Jinja e o fluxo de QR Code.
