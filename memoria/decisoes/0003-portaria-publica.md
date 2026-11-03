# ADR 0003 - Portaria sem senha

Em 03/11/2026 o usuario solicitou retirar o login da portaria.

Liberados /portaria, /api/checkin-portaria e /api/portaria/contagem-hoje.
Validacoes de QR, aluno ativo e duplicidade continuam nas operacoes de dados.
V2_AUTH_REQUIRED permanece true em producao para as demais areas protegidas.

O usuario autorizou tambem o envio do relatorio sem login administrativo.
Liberado somente /api/relatorio/gerar-agora, com POST e token CSRF da pagina.
O destino e o conteudo sao definidos no servidor; parametros do navegador nao
podem escolher outro telefone ou mensagem. O botao conserva a confirmacao.
Reserva atomica no banco bloqueia envios simultaneos e repeticao apos sucesso.
A mensagem de teste continua restrita ao administrador.
A cantina e suas APIs continuam exigindo perfil autorizado.

Consequencia: quem possui o endereco e um QR valido pode registrar entrada sem
identificacao do operador. A mudanca nao apaga registros nem altera credenciais.

Verificacao sem rede e sem gravacoes: scripts/testar_acesso_portaria.py.
Reserva diaria verificada em SQLite temporario com requisicoes concorrentes e
cliente Supabase simulado em scripts/testar_reserva_relatorio.py. Sem migracao
adicional: utiliza status, mensagem e updated_at ja existentes.
