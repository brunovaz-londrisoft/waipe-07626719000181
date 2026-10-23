---
name: waipe-revisar-modelos
description: Revisão (semanal) do catálogo de modelos do framework a partir dos agentes dos clientes (repositórios próprios e compartilhados): compara nome e fluxo, traz os modelos que faltam descaracterizados e no padrão de e-mail Waipe, publica o framework e atualiza os clientes. Use no template quando o usuário pedir "revisa os modelos", "atualiza o catálogo", "revisão semanal".
---

# Revisar os modelos do catálogo

Roda só no repositório template. Siga **`.claude/waipe/catalogo/ATUALIZAR-MODELOS.md`** do começo ao fim: é a rotina
completa (regras, comparação, escolha, como trazer cada modelo e como publicar).

Resumo:

1. Leia `.claude/waipe/catalogo/REVISOES.md` (última revisão e versões já adotadas).
2. `python3 .claude/waipe/waipe.py comparar-catalogo --json`: compara cada agente publicado de todos os repositórios
   `waipe-*` da conta (próprios, de organização e compartilhados) com o catálogo, pelo nome **e pelo fluxo**.
3. Traga para o catálogo os que ainda não existem (`novo`; `mesmo nome, fluxo diferente` vira `<slug>-2`, "(2)", e assim
   por diante): descaracterize, corrija os problemas conhecidos, monte os e-mails com o kit Waipe, escreva o `.md`, o
   `gerar_modelos.py`, rode `waipe.py gerar-modelos <slug>` e `waipe.py registrar-origem <slug> <dono/repo> <agente>`.
4. Melhorias de modelo existente e casos de dúvida: tabela para o usuário decidir.
5. `INDICE.md`, `README.md`, `REVISOES.md`, CHANGELOG; `waipe.py validar`, commit, `salvar`, `release-framework minor`
   e atualize os clientes (skill `waipe-atualizar-framework`).

Nunca crie catálogo em repositório de cliente ou compartilhado e nunca altere os flows de produção dos clientes.
