---
name: waipe-novo-cliente
description: Cria o repositório de um cliente novo (waipe-<cnpj>, com agentes e páginas) a partir do template waipe-template. Use quando o usuário pedir "cria o repositório do cliente X" ou "novo cliente". Roda no template.
---

# Novo cliente

1. Pergunte o nome do cliente (como aparece para pessoas) e o CNPJ, e sugira o repositório `waipe-<cnpj só números>`
   (ex.: `waipe-12345678000199`), o padrão dos clientes. Confirme dono (padrão: `brunovaz-londrisoft`) e que é privado.
2. `python3 .claude/waipe/waipe.py novo-cliente <repo> "<Nome do cliente>"`: cria o repositório privado a partir
   do template, clona ao lado do template, preenche `CLAUDE.md` e `README.md`, põe o tópico `waipe-cliente`. Só existe
   a branch `main`.
3. Responda com o link e a pasta local. Sugira anotar em `CLAUDE.md` as particularidades do cliente (ERP, empresas,
   destinatários, URL do Waipe Páginas) e começar o primeiro agente (`waipe-criar-agente`) ou a primeira página
   (`waipe-criar-plugin`) dentro da pasta nova. O repositório já vem com `agentes/`, `plugins/` e o catálogo `modelos/`.
