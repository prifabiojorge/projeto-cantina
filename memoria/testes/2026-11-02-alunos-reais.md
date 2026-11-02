# Substituicao dos dados de teste

Usuario confirmou explicitamente que todos os alunos e historicos eram de teste
e autorizou sua exclusao no SQLite e no Supabase.

Lista local validada: 293 alunos, em 10 turmas, todos em tempo integral.
Identificadores internos no formato 2026-TURMA-CHAMADA, pois a fonte nao informa
matriculas oficiais. Nomes e QR hashes nao sao registrados nesta memoria.

Backup anterior a exclusao: backups/20261102_192317/ (ignorado pelo Git).

Conferencia realizada por leitura dos dois bancos apos executar a substituicao:
- alunos: 293 em cada banco;
- checkin_portaria: 0;
- checkin_cantina: 0;
- liberacoes_forcadas: 0;
- relatorios_enviados: 0.

Configuracoes atualizadas para Escola Estadual Celso Rodrigues, turmas reais e
Integral. Perfis administrativos preservados. Nenhum deploy realizado.
O corte das rotas legadas para Supabase continua pendente; o site na Vercel
ainda pode apresentar dados vazios por usar SQLite temporario.
