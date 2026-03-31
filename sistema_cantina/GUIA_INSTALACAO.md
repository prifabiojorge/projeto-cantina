# Guia de Instalação — Sistema da Cantina
## CISEB Celso Rodrigues
### Santo Antônio do Tauá - PA

---

**Desenvolvido por:** Professor Fábio Fabuloso
**Contato:** WhatsApp (91) 98514-0988

---

## Requisitos
- 1 notebook Windows 10/11 (servidor - fica na secretaria)
- 2 notebooks ou tablets com Chrome (portaria e cantina)
- Rede Wi-Fi da escola (todos no mesmo roteador)
- Python 3.8+ instalado no servidor

---

## 1. No Notebook Servidor (Secretaria)

### 1.1 Descobrir o IP Fixo

1. Pressione `Win + R`, digite `cmd` e pressione Enter
2. Digite: `ipconfig`
3. Procure por "Endereço IPv4" (ex: `192.168.1.100`)

```
Adaptador de Ethernet Ethernet:

   Sufixo DNS específico de conexão. . :
   Endereço IPv4. . . . . . . . . . . . . . : 192.168.1.100
   Máscara de sub-rede . . . . . . . . . . .: 255.255.255.0
   Gateway padrão . . . . . . . . . . . . . : 192.168.1.1
```

**Anote este número.** Será o endereço do servidor.

**Dica:** Para garantir que o IP não mude, acesse o roteador da escola
(normalmente `192.168.1.1` no navegador) e reserve este IP para o
endereço MAC do notebook servidor.

---

### 1.2 Liberar Firewall

1. Clique com botão direito no menu Iniciar → "Terminal (Admin)"
   ou "Prompt de Comando (Admin)"
2. Cole e execute:

```cmd
netsh advfirewall firewall add rule name="Cantina Flask" dir=in action=allow protocol=TCP localport=5000
```

3. Deve aparecer: `Ok.`

---

### 1.3 Instalar Dependências

1. Abra o CMD na pasta do projeto
2. Execute:

```cmd
pip install -r requirements.txt
```

3. Aguarde instalar todos os pacotes (pode demorar alguns minutos)

---

### 1.4 Iniciar o Sistema

1. No CMD, na pasta do projeto, execute:

```cmd
python app.py
```

2. Deve aparecer:

```
 * Running on all addresses (0.0.0.0)
 * Running on https://127.0.0.1:5000
 * Running on https://192.168.1.100:5000
```

**NÃO feche esta janela.** Se fechar, o sistema para.

Para testar localmente, acesse no navegador do próprio servidor:
`https://localhost:5000`

---

### 1.5 Criar Atalho na Área de Trabalho

1. Clique com botão direito na Área de Trabalho → Novo → Atalho
2. No campo "Digite a localização do item":

```cmd
cmd /k "cd /d C:\caminho\do\projeto && python app.py"
```

(substitua `C:\caminho\do\projeto` pelo caminho real)

3. Clique "Avançar" → nomeie como "Iniciar Cantina"
4. Clique em "Concluir"
5. (Opcional) Clique com botão direito no atalho → Propriedades →
   Alterar ícone → escolha um ícone de sua preferência

---

## 2. No Notebook da Portaria

### 2.1 Abrir o Chrome

1. Abra o Google Chrome
2. Na barra de endereço, digite:

```
https://192.168.1.100:5000/portaria
```

(substitua `192.168.1.100` pelo IP real do servidor)

3. O Chrome mostrará um aviso de segurança:

```
Sua conexão não é particular
Os invasores podem estar tentando roubar suas informações de 192.168.1.100.
```

4. Clique em **"Avançado"**
5. Clique em **"Ir para 192.168.1.100 (não seguro)"**

**Por que isso acontece?** O certificado é autoassinado (gerado pelo
próprio sistema). É seguro usar na rede interna da escola. O HTTPS é
necessário para que o navegador permita acesso à câmera.

---

### 2.2 Permitir Câmera

1. O Chrome mostrará um popup: "192.168.1.100 deseja usar sua câmera"
2. Clique em **"Permitir"**
3. Se aparecer uma seleção de câmera, escolha a webcam desejada
4. A imagem da câmera deve aparecer no retângulo preto do scanner

**Se a câmera não aparecer:**
- Verifique se a webcam está conectada
- Clique no ícone de cadeado na barra de endereço →
  Configurações do site → Câmera → "Permitir"

---

### 2.3 Fixar a Aba

1. Clique com botão direito na aba da portaria
2. Selecione **"Fixar aba"**
3. A aba ficará menor e não poderá ser fechada acidentalmente

---

### 2.4 Modo Tela Cheia

1. Pressione **F11** para entrar em modo tela cheia
2. Para sair, pressione F11 novamente ou mova o mouse para o
   topo da tela e clique no X

**Dica:** Configure o notebook para não desligar a tela:
- Configurações → Sistema → Energia e suspensão → "Nunca"

---

## 3. No Notebook da Cantina

### 3.1 Abrir o Chrome

1. Abra o Google Chrome
2. Na barra de endereço, digite:

```
https://192.168.1.100:5000/cantina
```

3. Aceite o certificado (mesmo procedimento da portaria)
4. Permita o acesso à câmera

---

### 3.2 Ativar o Áudio

1. Clique no botão **"Iniciar Scanner"**
2. Isso ativa o áudio do navegador (necessário para os alarmes)
3. Clique em **"Testar Alarme"** para verificar se o som está funcionando
4. O alarme deve soar e o indicador deve ficar vermelho

**IMPORTANTE:** Se não clicar em "Iniciar Scanner", os alarmes
sonoros não funcionarão (política de autoplay do navegador).

---

### 3.3 Testar com QR Code

1. Pegue o QR code de um aluno (impresso ou no celular)
2. Posicione diante da câmera
3. O sistema deve:
   - Mostrar o nome do aluno em verde (se liberado)
   - Tocar um bip curto de confirmação
4. Tente o mesmo QR code novamente:
   - O sistema deve mostrar "Aluno já almoçou hoje" em amarelo
   - O alarme sonoro deve tocar (sirene)
   - A tela deve piscar em vermelho
5. Clique em **"Dispensar Alarme"** para parar a sirene

---

### 3.4 Configurações Recomendadas

- Fixe a aba (botão direito → Fixar aba)
- Use modo tela cheia (F11)
- Configure o notebook para não suspender:
  - Configurações → Sistema → Energia → "Nunca"
- Mantenha o volume do notebook em 50-70%

---

## 4. Teste de Comunicação

Após configurar os três notebooks, faça este teste:

### 4.1 No notebook do servidor:
- Acesse `https://localhost:5000/dashboard`
- Verifique se os gráficos carregam
- Anote os valores atuais (ex: "Portaria: 0, Cantina: 0")

### 4.2 No notebook da portaria:
- Escaneie o QR code de um aluno
- Verifique se aparece "Check-in registrado com sucesso"
- Note que o bip sonoro deve tocar

### 4.3 No notebook do servidor:
- Atualize o dashboard (F5)
- O valor de "Check-ins Portaria" deve ter aumentado em 1

### 4.4 No notebook da cantina:
- Escaneie o mesmo QR code
- Verifique se aparece "Aluno autorizado! Bom apetite."
- Note que o bip de sucesso deve tocar

### 4.5 No notebook do servidor:
- Atualize o dashboard
- O valor de "Check-ins Cantina" deve ter aumentado em 1

### 4.6 Verificar barra inferior na cantina:
- Deve mostrar: "Almoçaram: X/Y │ Hora: HH:MM │ Percentual: Z%"

---

## 5. Problemas Comuns

### "Não consigo acessar o servidor"
- Verifique se todos estão na mesma rede Wi-Fi
- Verifique se o firewall foi liberado (passo 1.2)
- No servidor, execute `ipconfig` e confirme o IP
- Tente pingar: `ping 192.168.1.100` (do notebook da portaria)

### "Câmera não funciona"
- Verifique se clicou "Permitir" quando o Chrome pediu
- Clique no ícone de cadeado na barra de endereço →
  Câmera → "Permitir"
- Teste com outra webcam (USB)
- Reinicie o Chrome

### "Alarme não toca"
- Clique em "Iniciar Scanner" primeiro (ativa o áudio)
- Verifique se o volume do notebook não está mudo
- Clique em "Testar Alarme" para verificar

### "Página não carrega"
- Verifique se o servidor está rodando (janela CMD aberta)
- Verifique se o IP está correto
- Tente acessar `https://localhost:5000` no próprio servidor

### "Certificado não confiável"
- Isso é normal. Clique "Avançado" → "Ir para... (não seguro)"
- O certificado é autoassinado, seguro para rede interna

### "Aluno não reconhecido"
- Verifique se o QR code está legível (não danificado)
- Verifique se o aluno está cadastrado no sistema
- Acesse `/alunos` no servidor para verificar

### "Relatório não envia"
- O WhatsApp precisa estar configurado em `/configuracoes`
- Sem configuração, o relatório é salvo em `relatorios_log.txt`
- Verifique o arquivo na pasta do projeto

### "Sistema lento"
- Reinicie o servidor (CTRL+C no CMD, depois `python app.py`)
- Verifique se há muitos processos Python rodando
- Limpe o cache do Chrome (Ctrl+Shift+Del)

---

## 6. Manutenção Diária

### 6.1 Backup
- Copie o arquivo `cantina.db` para um pendrive ou nuvem
- Recomendado: fazer backup toda sexta-feira

### 6.2 Limpeza
- A cada 30 dias, delete registros antigos do banco
- Consulte o administrador do sistema

### 6.3 Reinício
- Reinicie o servidor uma vez por semana
- Desligue o notebook à noite se não houver uso noturno

---

## 7. Contatos de Suporte

- **Desenvolvedor:** Professor Fábio Fabuloso
- **WhatsApp:** (91) 98514-0988
- **Escola:** CISEB Celso Rodrigues - Santo Antônio do Tauá - PA

Para dúvidas, sugestões ou problemas:
1. Envie mensagem pelo WhatsApp
2. Informe qual notebook está com problema (servidor/portaria/cantina)
3. Descreva o que aconteceu e qual mensagem de erro apareceu

---

*Última atualização: Março 2026*
*Sistema versão 2.0*
*Desenvolvido por Professor Fábio Fabuloso para CISEB Celso Rodrigues*
