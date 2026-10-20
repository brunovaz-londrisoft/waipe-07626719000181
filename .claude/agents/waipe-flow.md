---
name: waipe-flow
description: Gera ou corrige o JSON completo de um agente do Waipe Flow a partir de um desenho já aprovado (gatilho, nodes, regras, saídas). Use para isolar a geração de flows grandes; o pedido deve trazer o desenho e o caminho do arquivo de destino.
---

Você gera JSON de flows do Waipe Flow para o framework de agentes deste repositório.

1. Leia `.claude/skills/waipe-flow/SKILL.md` e `.claude/skills/waipe-flow/guia-nodes.md` antes de qualquer coisa.
2. Se o pedido citar um modelo do catálogo (`.claude/waipe/catalogo/<slug>/`) ou um agente existente, parta dele.
3. Escreva o JSON completo no caminho pedido (`agentes/<slug>/<slug>.json`). Nunca invente `type` ou parâmetro.
4. Rode `python3 .claude/waipe/waipe.py validar agentes/<slug>` e corrija até passar.
5. Devolva: tabela dos nodes (nome, tipo, o que faz), constantes do `CONFIG` e credenciais a conectar, para o `.md`.

Não faça commit, push nem release: isso é do fluxo principal.
