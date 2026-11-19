# Waipe: agentes e páginas

Cliente: IVAN ALEX MANDUCA

> Se a linha acima diz PENDENTE e este repositório **não** é o template `brunovaz-londrisoft/waipe-template`,
> pergunte o nome do cliente e rode `python3 .claude/waipe/waipe.py iniciar "<Nome do cliente>"`.
> Se este **é** o template, você está mantendo o framework: siga a seção "Repositório template" de `.claude/rules/waipe-gitflow.md`.

Este repositório guarda os agentes (flows do Waipe Flow, em `agentes/`) e as páginas (plugins do Waipe Páginas, em
`plugins/`) do cliente. O catálogo de modelos dos dois fica em `modelos/`. As regras do framework estão em
`.claude/rules/` e são carregadas sozinhas. Este arquivo é do cliente: o framework nunca o sobrescreve.

## Particularidades do cliente

Anote aqui o que vale só para este cliente: ERP e empresas do grupo, destinatários padrão, planilhas e pastas fixas,
nomes de vendedores ou regras de negócio, URL do Waipe Páginas do cliente e menus usados, pegadinhas descobertas nos
testes.

- Waipe Páginas: as páginas Pendências de Ontem, Cobrança em Aberto e Olho no Estoque (pasta `plugins/`) ficam no
  projeto Vercel `waipe-paginas` (https://waipe-paginas-hazel.vercel.app), alimentadas pelos flows que cada página
  gera em Configurações > Integração. Os agentes `cobranca-em-aberto` e `olho-no-estoque` viraram essas páginas.
