# Scanner ampliado na cantina

Aplicados os ajustes ja utilizados na portaria: area total do video sem qrbox,
15 tentativas por segundo, somente QR Code, resolucao preferencial 1280x720 e
foco continuo solicitado apenas se suportado. A previa nao usa altura fixa
que corte o video.

O proximo aluno pode ser lido ao concluir a resposta; apenas a repeticao do
mesmo QR conserva intervalo de dois segundos. Durante a liberacao manual,
outra leitura fica bloqueada ate a conclusao, preservando o aluno selecionado.

Verificacoes:
- scripts/testar_scanner_cantina.cjs: configuracao, foco opcional, requisicoes
  simultaneas, proximo aluno, duplicidade, sucesso, alarme, liberacao manual e
  recuperacao de falhas;
- scripts/testar_scanner_portaria.cjs: regressao passou;
- Chrome headless com leitor 2.3.8 e video sintetico: QR proximo da borda foi
  reconhecido em larguras 1366 e 390, sem recorte ou overflow horizontal;
- screenshots inspecionadas em backups/inspecao_pdf, fora do Git.

Nenhum acesso ao Supabase, mensagem real, alteracao de login ou deploy.
Foco, nitidez e velocidade na camera fisica ainda dependem do equipamento.
