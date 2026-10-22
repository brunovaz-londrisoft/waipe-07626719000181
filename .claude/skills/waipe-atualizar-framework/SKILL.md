---
name: waipe-atualizar-framework
description: Atualiza o framework Waipe num repositório de cliente (ou em todos os clientes, quando rodada no template) sem tocar nos agentes. Use quando o usuário pedir "atualiza o framework", "puxa a versão nova do template", "atualiza todos os clientes".
---

# Atualizar o framework

## Num repositório de cliente

1. `python3 .claude/waipe/waipe.py status` (versão atual) e
   `gh release view -R brunovaz-londrisoft/waipe-agentes-template` (versão nova e notas).
2. Mostre ao usuário o que muda (CHANGELOG entre as duas). Versão maior pode pedir ação: diga qual.
3. Com o ok, `python3 .claude/waipe/waipe.py atualizar` (ou `atualizar vX.Y.Z`). O script troca só os arquivos do
   framework, aborta se algo fora de `.claude/` e `.github/` mudar e grava direto na `main`.
4. Se o repositório ainda tem `develop` (vindo de antes da v2.0.0), rode `python3 .claude/waipe/waipe.py migrar`
   depois de atualizar: apaga `develop` e deixa só a `main`.
5. Se a versão maior pedir outra ação no cliente, faça na `main` e `salvar`.
6. **Vindo de antes da v3.0.0** com modelos de comunicação na estrutura antiga (`agentes/modelos/<slug>/` ou `modelos/<slug>/`
   na raiz, com `index.html`): leve as peças de cada agente para `agentes/<slug>/modelos/` no formato da v3
   (`.claude/waipe/modelos-comunicacao/PADRAO.md`): o e-mail fica só com o HTML enviado (sem a moldura de apresentação),
   o WhatsApp vira `pagina_whatsapp` com o mesmo texto, as planilhas viram `pagina_planilha` e o PDF é copiado. Grave o
   `modelos.json`, apague a pasta antiga (com o `index.html` e o `README.md`), rode `validar`, commit
   `docs: modelos de comunicação no formato v3` e `salvar`. Os dados e o desenho continuam os do cliente.

## No template (todos os clientes)

1. `python3 .claude/waipe/waipe.py clientes` lista os repositórios com o tópico `waipe-cliente`.
2. Mostre a lista e confirme com o usuário quais atualizar.
3. Para cada um: use o clone em `../<repo>` se existir e estiver limpo, senão clone com
   `gh repo clone <repo> <pasta-temporária>`; rode `python3 .claude/waipe/waipe.py atualizar` dentro dele.
4. Relate uma linha por cliente: versão anterior → nova, ou o erro.
