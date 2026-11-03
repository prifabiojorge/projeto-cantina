"""Verifica envio sem rede, mensagens reais ou gravacoes no banco."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sistema_cantina'))
import whatsapp_sender as wa
import models

env = dict(WHATSAPP_ENABLED='true', WHATSAPP_METHOD='callmebot',
           WHATSAPP_PHONE_NUMBER='5591999999999', CALLMEBOT_API_KEY='chave-ficticia')
with patch.dict(os.environ, env), patch.object(wa, '_get_config', return_value={}), patch.object(wa, 'enviar_whatsapp_callmebot', return_value=True) as enviar:
    assert wa.enviar_whatsapp('', 'teste') is True
    enviar.assert_called_once_with(env['WHATSAPP_PHONE_NUMBER'], 'chave-ficticia', 'teste')
    enviar.reset_mock()
    with patch.dict(os.environ, WHATSAPP_ENABLED='false'):
        assert wa.enviar_whatsapp('', 'teste') is False
        enviar.assert_not_called()
    with patch.dict(os.environ, CALLMEBOT_API_KEY=''):
        assert wa.enviar_whatsapp('', 'teste') is False
        enviar.assert_not_called()

for resposta, esperado in [('Message queued', True), ('Error 200: invalid API key', False)]:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = resposta.encode()
    with patch.object(wa.urllib.request, 'urlopen', return_value=response) as http, patch.object(wa.time, 'sleep'):
        assert wa.enviar_whatsapp_callmebot('5591999999999', 'teste', 'teste') is esperado
        assert http.call_count == (1 if esperado else 3)

with patch.object(models, 'relatorio_ja_enviado_hoje', return_value=False), patch.object(models, 'gerar_relatorio_portaria_hoje', return_value={'total':1, 'texto_detalhes':''}), patch.object(models, 'registrar_relatorio_enviado') as registrar, patch.object(wa, 'enviar_relatorio_diario', return_value=False), patch('builtins.open', MagicMock()):
    sucesso, _ = models.enviar_relatorio_whatsapp_agora()
    assert sucesso is False
    assert registrar.call_args.kwargs['status'] == 'falha'
print('OK: configuracao por ambiente, desabilitado, credencial ausente, confirmacao do provedor e falha sem marcar enviado.')
