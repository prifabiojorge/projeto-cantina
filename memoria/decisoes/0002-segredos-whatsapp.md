# ADR 0002 - Segredos do WhatsApp somente por ambiente

Data: 2026-05-18

## Decisão

`CALLMEBOT_API_KEY` não deve ficar em `config_escola.json` nem em arquivos versionados.
A chave passa a ser lida somente de variável de ambiente. O telefone pode ser
definido por `WHATSAPP_PHONE_NUMBER`, com fallback local para configuração sem
segredo.

## Consequências

- Deploy Vercel deve configurar `CALLMEBOT_API_KEY`, `WHATSAPP_PHONE_NUMBER` e
  `WHATSAPP_ENABLED=true` quando o envio real estiver validado.
- Exportação de configurações remove `callmebot_apikey` caso exista em arquivo
  legado.
- `sistema_cantina/config_escola.json` foi saneado para não carregar a chave
  histórica.
