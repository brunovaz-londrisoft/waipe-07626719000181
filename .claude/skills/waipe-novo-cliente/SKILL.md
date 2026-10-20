---
name: waipe-novo-cliente
description: Cria o repositório de agentes de um cliente novo a partir do template waipe-agentes-template. Use quando o usuário pedir "cria o repositório do cliente X" ou "novo cliente". Roda no template.
---

# Novo cliente

1. Pergunte o nome do cliente (como aparece para pessoas) e sugira o repositório `waipe-<slug-do-cliente>`
   (ex.: "Distribuidora Alfa" → `waipe-distribuidora-alfa`). Confirme dono (padrão: `brunovaz-londrisoft`) e que é privado.
2. `python3 .claude/waipe/waipe.py novo-cliente <repo> "<Nome do cliente>"`: cria o repositório privado a partir
   do template, clona ao lado do template, preenche `CLAUDE.md` e `README.md`, põe o tópico `waipe-cliente`. Só existe
   a branch `main`.
3. Responda com o link e a pasta local. Sugira anotar em `CLAUDE.md` as particularidades do cliente (ERP, empresas,
   destinatários) e começar o primeiro agente com `waipe-criar-agente` dentro da pasta nova.
