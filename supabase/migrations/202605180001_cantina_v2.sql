create extension if not exists pgcrypto;

create table if not exists public.perfis_usuarios (
  user_id uuid primary key references auth.users(id) on delete cascade,
  nome text,
  papel text not null default 'admin' check (papel in ('admin', 'portaria', 'cantina')),
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.alunos (
  id uuid primary key default gen_random_uuid(),
  legacy_id integer,
  nome text not null check (length(trim(nome)) > 0),
  matricula text not null unique,
  turma text not null,
  turno text not null,
  qrcode_hash text not null unique,
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.checkin_portaria (
  id uuid primary key default gen_random_uuid(),
  aluno_id uuid not null references public.alunos(id) on delete cascade,
  data date not null default current_date,
  hora_checkin timestamptz not null default now(),
  usuario_id uuid references auth.users(id) on delete set null default auth.uid(),
  origem text not null default 'scanner',
  created_at timestamptz not null default now(),
  unique (aluno_id, data)
);

create table if not exists public.checkin_cantina (
  id uuid primary key default gen_random_uuid(),
  aluno_id uuid not null references public.alunos(id) on delete cascade,
  data date not null default current_date,
  hora_almoco timestamptz not null default now(),
  usuario_id uuid references auth.users(id) on delete set null default auth.uid(),
  origem text not null default 'scanner',
  created_at timestamptz not null default now(),
  unique (aluno_id, data)
);

create table if not exists public.liberacoes_forcadas (
  id uuid primary key default gen_random_uuid(),
  aluno_id uuid not null references public.alunos(id) on delete cascade,
  data date not null default current_date,
  motivo text not null check (length(trim(motivo)) >= 3),
  usuario_id uuid references auth.users(id) on delete set null default auth.uid(),
  usuario_responsavel text,
  criado_em timestamptz not null default now(),
  unique (aluno_id, data)
);

create table if not exists public.relatorios_enviados (
  id uuid primary key default gen_random_uuid(),
  data date not null unique,
  total_esperado integer not null default 0 check (total_esperado >= 0),
  enviado_em timestamptz,
  status text not null default 'pendente' check (status in ('pendente', 'enviado', 'falhou', 'simulado')),
  mensagem text,
  detalhes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.configuracoes (
  id uuid primary key default gen_random_uuid(),
  chave text not null unique,
  valor text,
  descricao text,
  atualizado_em timestamptz not null default now()
);

create index if not exists alunos_turma_turno_idx on public.alunos (turma, turno) where ativo = true;
create index if not exists checkin_portaria_data_idx on public.checkin_portaria (data);
create index if not exists checkin_cantina_data_idx on public.checkin_cantina (data);
create index if not exists liberacoes_forcadas_data_idx on public.liberacoes_forcadas (data);
create index if not exists relatorios_status_data_idx on public.relatorios_enviados (status, data);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists perfis_usuarios_set_updated_at on public.perfis_usuarios;
create trigger perfis_usuarios_set_updated_at
before update on public.perfis_usuarios
for each row execute function public.set_updated_at();

drop trigger if exists alunos_set_updated_at on public.alunos;
create trigger alunos_set_updated_at
before update on public.alunos
for each row execute function public.set_updated_at();

drop trigger if exists relatorios_enviados_set_updated_at on public.relatorios_enviados;
create trigger relatorios_enviados_set_updated_at
before update on public.relatorios_enviados
for each row execute function public.set_updated_at();

create or replace function public.current_user_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select papel
  from public.perfis_usuarios
  where user_id = auth.uid()
    and ativo = true
  limit 1
$$;

alter table public.perfis_usuarios enable row level security;
alter table public.alunos enable row level security;
alter table public.checkin_portaria enable row level security;
alter table public.checkin_cantina enable row level security;
alter table public.liberacoes_forcadas enable row level security;
alter table public.relatorios_enviados enable row level security;
alter table public.configuracoes enable row level security;

grant usage on schema public to authenticated;
grant select, insert, update, delete on all tables in schema public to authenticated;

drop policy if exists perfis_admin_all on public.perfis_usuarios;
create policy perfis_admin_all on public.perfis_usuarios
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists perfis_self_read on public.perfis_usuarios;
create policy perfis_self_read on public.perfis_usuarios
for select using (user_id = auth.uid());

drop policy if exists alunos_admin_all on public.alunos;
create policy alunos_admin_all on public.alunos
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists alunos_operacao_read on public.alunos;
create policy alunos_operacao_read on public.alunos
for select using (public.current_user_role() in ('admin', 'portaria', 'cantina'));

drop policy if exists portaria_admin_all on public.checkin_portaria;
create policy portaria_admin_all on public.checkin_portaria
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists portaria_operador_insert on public.checkin_portaria;
create policy portaria_operador_insert on public.checkin_portaria
for insert with check (public.current_user_role() in ('admin', 'portaria'));

drop policy if exists portaria_operador_read on public.checkin_portaria;
create policy portaria_operador_read on public.checkin_portaria
for select using (public.current_user_role() in ('admin', 'portaria', 'cantina'));

drop policy if exists cantina_admin_all on public.checkin_cantina;
create policy cantina_admin_all on public.checkin_cantina
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists cantina_operador_insert on public.checkin_cantina;
create policy cantina_operador_insert on public.checkin_cantina
for insert with check (public.current_user_role() in ('admin', 'cantina'));

drop policy if exists cantina_operador_read on public.checkin_cantina;
create policy cantina_operador_read on public.checkin_cantina
for select using (public.current_user_role() in ('admin', 'cantina'));

drop policy if exists liberacoes_admin_all on public.liberacoes_forcadas;
create policy liberacoes_admin_all on public.liberacoes_forcadas
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists liberacoes_cantina_insert on public.liberacoes_forcadas;
create policy liberacoes_cantina_insert on public.liberacoes_forcadas
for insert with check (public.current_user_role() in ('admin', 'cantina'));

drop policy if exists liberacoes_cantina_read on public.liberacoes_forcadas;
create policy liberacoes_cantina_read on public.liberacoes_forcadas
for select using (public.current_user_role() in ('admin', 'cantina'));

drop policy if exists relatorios_admin_all on public.relatorios_enviados;
create policy relatorios_admin_all on public.relatorios_enviados
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

drop policy if exists configuracoes_admin_all on public.configuracoes;
create policy configuracoes_admin_all on public.configuracoes
for all using (public.current_user_role() = 'admin')
with check (public.current_user_role() = 'admin');

insert into storage.buckets (id, name, public)
values
  ('qrcodes', 'qrcodes', false),
  ('relatorios', 'relatorios', false),
  ('backups', 'backups', false)
on conflict (id) do nothing;

drop policy if exists storage_admin_all_qrcodes on storage.objects;
create policy storage_admin_all_qrcodes on storage.objects
for all using (
  bucket_id in ('qrcodes', 'relatorios', 'backups')
  and public.current_user_role() = 'admin'
)
with check (
  bucket_id in ('qrcodes', 'relatorios', 'backups')
  and public.current_user_role() = 'admin'
);

drop policy if exists storage_operacao_read_qrcodes on storage.objects;
create policy storage_operacao_read_qrcodes on storage.objects
for select using (
  bucket_id = 'qrcodes'
  and public.current_user_role() in ('admin', 'portaria', 'cantina')
);
