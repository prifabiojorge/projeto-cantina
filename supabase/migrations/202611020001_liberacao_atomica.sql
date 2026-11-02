-- A refeicao e sua justificativa sao gravadas na mesma transacao.
create or replace function public.cantina_liberar(
  p_hash text, p_motivo text, p_responsavel text, p_data date
) returns jsonb language plpgsql security definer set search_path = public as $$
declare a public.alunos; resultado text;
begin
  if length(trim(p_motivo)) < 3 then
    return jsonb_build_object('status','motivo_invalido','aluno',null);
  end if;
  select * into a from public.alunos where qrcode_hash=p_hash for update;
  if not found then return jsonb_build_object('status','nao_encontrado','aluno',null); end if;
  if not a.ativo then return jsonb_build_object('status','inativo','aluno',to_jsonb(a)); end if;
  if exists(select 1 from public.checkin_cantina where aluno_id=a.id and data=p_data) then
    return jsonb_build_object('status','ja_almocou','aluno',to_jsonb(a));
  end if;
  begin
    insert into public.checkin_cantina(aluno_id,data,origem) values(a.id,p_data,'liberacao_forcada');
    insert into public.liberacoes_forcadas(aluno_id,data,motivo,usuario_responsavel)
      values(a.id,p_data,trim(p_motivo),p_responsavel);
    resultado := 'liberado_forcado';
  exception when unique_violation then resultado := 'ja_almocou';
  end;
  return jsonb_build_object('status',resultado,'aluno',to_jsonb(a),'motivo',p_motivo,'usuario_responsavel',p_responsavel);
end $$;
revoke all on function public.cantina_liberar(text,text,text,date) from public, anon, authenticated;
grant execute on function public.cantina_liberar(text,text,text,date) to service_role;
