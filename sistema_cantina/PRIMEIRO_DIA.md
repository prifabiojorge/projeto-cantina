# 🍽️ Checklist do Primeiro Dia — Sistema da Cantina
## CISEB Celso Rodrigues — Santo Antônio do Tauá - PA

**Responsável:** Professor Fábio Fabuloso
**WhatsApp:** (91) 98514-0988

---

## Na Véspera (Dia Anterior)

- [ ] Alunos cadastrados no sistema? (Quantos: ___)
- [ ] QR codes impressos e plastificados?
- [ ] QR codes distribuídos para os alunos?
- [ ] Os 3 notebooks estão carregados?
- [ ] Os 3 notebooks conectam no Wi-Fi da escola?
- [ ] O notebook servidor está com IP fixo configurado?
- [ ] Firewall liberado na porta 5000?
- [ ] Teste rápido: abrir https://IP-SERVIDOR:5000 no navegador

---

## 06:00 — Ligar o Sistema

- [ ] Ligar notebook servidor (secretaria)
- [ ] Abrir CMD → `cd pasta do projeto` → `python app.py`
- [ ] Verificar: apareceu "Running on https://0.0.0.0:5000"?
- [ ] Abrir Chrome no servidor → https://localhost:5000/dashboard
- [ ] Dashboard carregou com dados zerados (início do dia)?
- [ ] Verificar horário do servidor está correto

---

## 06:15 — Ligar Portaria

- [ ] Ligar notebook da portaria
- [ ] Chrome → https://IP-SERVIDOR:5000/portaria
- [ ] Aceitar certificado ("Avançado" → "Continuar")
- [ ] Câmera funcionou? Scanner apareceu?
- [ ] Testar: escanear QR code de um aluno de teste
- [ ] Check-in registrou? Contador incrementou?
- [ ] Pressionar F11 (tela cheia)
- [ ] Fixar a aba (botão direito → Fixar aba)

---

## 06:15 — Ligar Cantina (pode fazer depois)

- [ ] Ligar notebook da cantina
- [ ] Chrome → https://IP-SERVIDOR:5000/cantina
- [ ] Aceitar certificado
- [ ] **Clicar "Iniciar Scanner"** (OBRIGATÓRIO para áudio funcionar)
- [ ] Testar: escanear QR code de aluno que JÁ fez check-in
- [ ] Apareceu LIBERADO (verde + bip)?
- [ ] Testar: escanear MESMO QR code de novo
- [ ] **ALARME TOCOU?** (sirene + tela vermelha piscando)
- [ ] Botão "Dispensar Alarme" funcionou?
- [ ] Scanner voltou ao normal?
- [ ] Pressionar F11 (tela cheia)
- [ ] Fixar a aba

---

## 06:30–07:30 — Operação da Portaria

- [ ] Porteiro escaneando QR codes dos alunos que vão almoçar
- [ ] Contador no canto superior mostra total crescente
- [ ] Se aluno esqueceu QR: anotar nome para cadastro manual depois
- [ ] Monitorar se a câmera está focada e bem iluminada

---

## 08:00 — Relatório Automático

- [ ] O sistema gerou o relatório?
- [ ] Verificar no dashboard: card "Relatório Enviado"
- [ ] Se WhatsApp configurado: mensagem chegou no grupo?
- [ ] Se WhatsApp NÃO configurado: verificar `relatorios_log.txt`
- [ ] Informar cozinha do total (verbalmente se necessário no primeiro dia)

---

## 11:30 — Operação da Cantina

- [ ] Funcionário da cantina com notebook pronto
- [ ] Scanner da cantina ativo
- [ ] Para CADA aluno na fila: escanear QR code
- [ ] Verde + bip = servir
- [ ] Amarelo = sem check-in, decidir se libera
- [ ] **VERMELHO + SIRENE = já almoçou, NÃO servir**
- [ ] Barra inferior mostrando contagem em tempo real
- [ ] Se alarme disparar: clicar "Dispensar Alarme"

---

## 13:00 — Fim do Almoço

- [ ] Verificar dashboard: quantos almoçaram vs. esperado
- [ ] Anotar observações para ajuste (problemas, sugestões)
- [ ] Verificar se todos os QR codes foram lidos corretamente

---

## 17:00 — Fim do Dia

- [ ] Desligar notebooks da portaria e cantina
- [ ] **NO SERVIDOR: NÃO fechar o CMD (deixar rodando)**
  OU: Ctrl+C para parar, e desligar
- [ ] Backup: copiar `cantina.db` para pendrive ou nuvem
- [ ] Guardar pendrive em local seguro

---

## Problemas Esperados no Primeiro Dia

| Problema | Solução |
|----------|---------|
| Aluno sem QR code | Anotar nome, cadastrar depois |
| Câmera não ativa | Verificar permissão do Chrome (ícone de cadeado) |
| Scanner não lê QR | QR code danificado, reimprimir |
| Alarme não toca | Clicar "Iniciar Scanner" de novo |
| Wi-Fi caiu | Reconectar; dados locais não perdem |
| Notebook do servidor desligou | Religar e executar `python app.py` |
| Página não carrega | Verificar IP do servidor com `ipconfig` |
| Certificado não confiável | Normal; clicar "Avançado" → "Continuar" |
| Aluno já registrado | Sistema bloqueia; não servir |
| Contagem errada | Atualizar dashboard (F5) |

---

## Contatos de Emergência

- **Desenvolvedor:** Professor Fábio Fabuloso
- **WhatsApp:** (91) 98514-0988
- **Escola:** CISEB Celso Rodrigues - Santo Antônio do Tauá - PA

**Em caso de problema grave:**
1. Não entre em pânico
2. Anote o que aconteceu
3. Tire foto da tela (se houver erro)
4. Envie mensagem pelo WhatsApp

---

## Observações do Primeiro Dia

```
Data: ___/___/2026

Total de alunos previsto: ___
Total que almoçaram: ___
Problemas encontrados:


Sugestões de melhoria:


Assinatura do responsável: _________________________
```

---

*Documento gerado em Março 2026*
*Desenvolvido por Professor Fábio Fabuloso para CISEB Celso Rodrigues*
