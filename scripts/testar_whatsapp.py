"""Verifica envio sem rede, mensagens reais ou gravacoes no banco."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sistema_cantina'))
import whatsapp_sender as wa
import models
check = TestCase()

env = dict(WHATSAPP_ENABLED='true', WHATSAPP_METHOD='callmebot',
           WHATSAPP_PHONE_NUMBER='5591999999999', CALLMEBOT_API_KEY='chave-ficticia')
with patch.dict(os.environ, env), patch.object(wa, '_get_config', return_value={}), patch.object(wa, 'enviar_whatsapp_callmebot', return_value=True) as enviar:
    assert wa.enviar_whatsapp('', 'teste') is True
    enviar.assert_called_once_with(env['WHATSAPP_PHONE_NUMBER'], 'chave-ficticia', 'teste')
    enviar.reset_mock()
    with patch.dict(os.environ, WHATSAPP_ENABLED='false'):
        with check.assertRaisesRegex(wa.WhatsAppError, 'WHATSAPP_ENABLED=true'):
            wa.enviar_whatsapp('', 'teste')
        enviar.assert_not_called()
    with patch.dict(os.environ, CALLMEBOT_API_KEY=''):
        with check.assertRaisesRegex(wa.WhatsAppError, 'CALLMEBOT_API_KEY ausente'):
            wa.enviar_whatsapp('', 'teste')
        enviar.assert_not_called()
    with patch.dict(os.environ, WHATSAPP_METHOD='CALLMEBOT', WHATSAPP_PHONE_NUMBER='+55 (91) 99999-9999'):
        assert wa.enviar_whatsapp('', 'teste') is True
        enviar.assert_called_once_with(env['WHATSAPP_PHONE_NUMBER'], 'chave-ficticia', 'teste')

for resposta, esperado in [('Message queued', True), ('<b>MESSAGE</b> queued', True), ('Error 200: invalid API key', False)]:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = resposta.encode()
    with patch.object(wa.urllib.request, 'urlopen', return_value=response) as http, patch.object(wa.time, 'sleep'):
        if esperado:
            assert wa.enviar_whatsapp_callmebot('5591999999999', 'teste', 'teste') is True
        else:
            with check.assertRaisesRegex(wa.WhatsAppError, 'rejeitou a chave'):
                wa.enviar_whatsapp_callmebot('5591999999999', 'teste', 'teste')
        assert http.call_count == 1

with patch.object(wa.urllib.request, 'urlopen', side_effect=wa.urllib.error.URLError('url-com-chave-secreta')) as http, patch.object(wa.time, 'sleep'):
    with check.assertRaisesRegex(wa.WhatsAppError, 'tres tentativas') as erro:
        wa.enviar_whatsapp_callmebot('5591999999999', 'teste', 'teste')
    assert 'secreta' not in str(erro.exception)
    assert http.call_count == 3

with patch.object(models, 'relatorio_ja_enviado_hoje', return_value=False), patch.object(models, 'gerar_relatorio_portaria_hoje', return_value={'total':1, 'texto_detalhes':''}), patch.object(models, 'registrar_relatorio_enviado') as registrar, patch.object(wa, 'enviar_relatorio_diario', return_value=False), patch('builtins.open', MagicMock()):
    sucesso, _ = models.enviar_relatorio_whatsapp_agora()
    assert sucesso is False
    assert registrar.call_args.kwargs['status'] == 'falha'
with patch.object(models, 'relatorio_ja_enviado_hoje', return_value=False), patch.object(models, 'gerar_relatorio_portaria_hoje', return_value={'total':1, 'texto_detalhes':''}), patch.object(models, 'registrar_relatorio_enviado') as registrar, patch.object(wa, 'enviar_relatorio_diario', side_effect=wa.WhatsAppError('Chave rejeitada')), patch('builtins.open', MagicMock()):
    sucesso, mensagem = models.enviar_relatorio_whatsapp_agora()
    assert sucesso is False and mensagem == 'Chave rejeitada'
    registrar.assert_called_once_with(1, status='falha', mensagem='Chave rejeitada')
print('OK: configuracao por ambiente, desabilitado, credencial ausente, confirmacao do provedor e falha sem marcar enviado.')
