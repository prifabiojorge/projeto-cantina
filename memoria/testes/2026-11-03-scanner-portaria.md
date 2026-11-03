# Area e resposta do scanner da portaria

Problema observado: QR Code parcialmente fora da moldura fixa de 500x500 e
pausa de dois segundos impedindo a leitura de qualquer aluno apos cada resposta.

Alteracoes:
- leitura de toda a imagem, sem qrbox central;
- previa ocupa a largura disponivel e nao tem altura fixa que corte o video;
- 15 tentativas de leitura por segundo, limitadas ao formato QR Code;
- resolucao preferencial 1280x720, sem exigir que a camera suporte HD;
- foco continuo solicitado apenas quando anunciado pela camera;
- libera o proximo aluno ao concluir a requisicao; o mesmo codigo conserva
  intervalo de dois segundos para evitar requisicoes repetidas a cada quadro.

Verificacoes:
- scripts/testar_scanner_portaria.cjs: configuracao, foco opcional, bloqueio de
  requisicoes simultaneas, proximo aluno, repeticao e recuperacao de erro HTTP;
- scripts/testar_som_portaria.cjs: sons preservados;
- Chrome headless com html5-qrcode 2.3.8 e video sintetico 1280x720: QR proximo
  da borda direita reconhecido nas larguras 1366 e 390; video sem recorte,
  pagina sem overflow horizontal e sem erros JavaScript;
- screenshots inspecionadas em backups/inspecao_pdf (fora do Git).

Os testes usaram servidor temporario com respostas ficticias, sem acesso ao
Supabase, envio de mensagens ou utilizacao de camera fisica. Nao houve deploy.
Velocidade e foco reais dependem da camera, iluminacao e tempo de resposta do banco.

API consultada: https://scanapp.org/html5-qrcode-docs/docs/apis/interfaces/Html5QrcodeCameraScanConfig
