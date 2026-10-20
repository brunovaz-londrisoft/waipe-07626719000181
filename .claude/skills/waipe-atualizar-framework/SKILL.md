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

## No template (todos os clientes)

1. `python3 .claude/waipe/waipe.py clientes` lista os repositórios com o tópico `waipe-cliente`.
2. Mostre a lista e confirme com o usuário quais atualizar.
3. Para cada um: use o clone em `../<repo>` se existir e estiver limpo, senão clone com
   `gh repo clone <repo> <pasta-temporária>`; rode `python3 .claude/waipe/waipe.py atualizar` dentro dele.
4. Relate uma linha por cliente: versão anterior → nova, ou o erro.
