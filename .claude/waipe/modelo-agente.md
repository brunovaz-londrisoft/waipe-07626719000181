---
nome: Nome legível do agente
slug: {{slug}}
versao: 0.0.0
modelo_base: nenhum
gatilho: manual
atualizado: {{data}}
---

# Nome legível do agente

## Objetivo

Uma ou duas frases: que problema do cliente este agente resolve e quem recebe o resultado.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Gatilho | trigger_manual | Quando e como o flow dispara. |

## Configuração após importar

- Credenciais a conectar no painel de cada node (Google, Z-API, tokens).
- Bloco `CONFIG` do node de código: o que cada constante controla.
- IDs externos (planilha, pasta, destinatários) que precisam ser trocados.

### Relatórios do Data Lab (textos para criar)

Se o flow usa `waipe_data` com Data Lab, registre aqui **o texto (prompt) de cada relatório**, exatamente como foi
criado no Data Lab, para poder recriá-lo em outro cliente ou ambiente. Um relatório por linha; no modelo de catálogo
não vai o ID, só o texto.

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| (nome do node) | (nome no Data Lab) | `texto do pedido, com os parâmetros {entre_chaves}` |

Se o texto tiver parâmetros (ex.: `{inicio_mes}`), diga que precisam de valor padrão. Se o flow não usa Data Lab, apague esta seção.

## Como testar

1. Importe `{{slug}}.json` no Waipe Flow (Dashboard → Importar JSON).
2. Conecte as credenciais e rode manualmente.
3. Resultado esperado: ...

## Histórico

### Não publicado
- Primeira versão.
