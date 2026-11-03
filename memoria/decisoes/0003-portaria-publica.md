# ADR 0003 - Portaria sem senha

Em 03/11/2026 o usuario solicitou retirar o login da portaria.

Liberados /portaria, /api/checkin-portaria e /api/portaria/contagem-hoje.
Validacoes de QR, aluno ativo e duplicidade continuam nas operacoes de dados.
V2_AUTH_REQUIRED permanece true em producao para as demais areas protegidas.

Os botoes de WhatsApp na portaria aparecem apenas com sessao administrativa.
A cantina e suas APIs continuam exigindo perfil autorizado.

Consequencia: quem possui o endereco e um QR valido pode registrar entrada sem
identificacao do operador. A mudanca nao apaga registros nem altera credenciais.

Verificacao sem rede e sem gravacoes: scripts/testar_acesso_portaria.py.
