# Impressao em lote

PDF fornecido pelo usuario apresentava sobreposicao de cinco paginas logicas em
duas folhas. Causa: position:absolute em todas as paginas de impressao.

Corrigido o fluxo de impressao para paginas sequenciais e grade fixa 2x4 em A4.
Teste com 35 alunos ficticios, QR embutido e Chrome headless (Playwright):
- PDF com 5 paginas;
- distribuicao de alunos: 8, 8, 8, 8, 3;
- primeira pagina renderizada e inspecionada sem sobreposicao.

Artefatos de inspecao ficam em backups/inspecao_pdf (fora do Git).
Nao foi realizado deploy nem teste em impressora fisica.
