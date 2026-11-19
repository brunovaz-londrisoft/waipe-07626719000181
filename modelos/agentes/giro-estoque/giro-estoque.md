---
nome: Giro de Estoque
slug: giro-estoque
versao: 1.4.0
modelo_base: nenhum
gatilho: agendado (segundas e quintas, 07:30, America/Sao_Paulo)
icone: 📦
resumo: Giro, cobertura e curva ABC por fabricante, com uma planilha por fabricante e o consolidado com o ranking de ação imediata.
frequencia: Segundas e quintas, 07:30
quem_recebe: Gestor
nota: Este fluxo envia só o consolidado ao gestor.
atualizado: 2026-10-29
---

# Giro de Estoque

## Quando usar

Cliente que quer saber **o que comprar e o que está parado**: calcula giro, cobertura e curva ABC de cada produto, cria uma
planilha por fabricante e manda ao gestor um consolidado com o ranking de quem tem mais produtos para ação imediata.

Palavras-chave: estoque, giro, cobertura, curva ABC, ruptura, compra, fabricante, sugestão de compra, estoque parado.

Modelos de comunicação (consolidado do gestor e planilha): `modelos/agentes/giro-estoque/modelos/` (lista das peças em `modelos.json`).

## Perguntas para personalizar

1. **Nome da empresa** e **nome do gestor** do e-mail, e o **e-mail do gestor**.
2. **Período de vendas** analisado (padrão: 90 dias) e **horizonte da sugestão de compra** (padrão: 45 dias).
3. **Cortes da curva ABC** (padrão: A até 80% do volume, B até 95%) e os **dias de cobertura** crítico, atenção e excesso de cada curva.
4. **Quando rodar** (padrão: segundas e quintas, 07:30).
5. **Estoque negativo** conta como zero na sugestão de compra?
6. O relatório de produtos traz o **fabricante**? Se não, o agrupamento cai em "Sem fabricante".
7. Aceita planilhas visíveis para quem tiver o link?

## Objetivo

Mostrar o que comprar e o que está parado: calcula saída por dia, cobertura em dias, sugestão de compra, curva ABC e
status/prioridade de cada produto a partir das vendas do período, **cria uma planilha do Google Sheets para cada fabricante**
e uma **planilha consolidada** com todos os produtos, e envia ao gestor um e-mail com o botão da consolidada, o ranking dos
fabricantes, o botão de cada planilha e a distribuição por status.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Segundas e quintas, 07:30 (`America/Sao_Paulo`). |
| 2 | Waipe Data | waipe_data | Relatório do Data Lab: produto, fabricante, estoque atual e quantidade vendida no período. |
| 3 | Giro do Estoque | code | Calcula saída por dia, cobertura, sugestão de compra, curva ABC (Pareto sobre a quantidade vendida de todos os produtos) e status/prioridade. |
| 4 | Montar Fabricantes | code | Agrupa por fabricante, conta ação imediata e sugestão, monta o ranking e o resumo por status. |
| 5 | Criar Planilha Índice | google_sheets (create) | Planilha-índice da execução, para guardar o link de cada fabricante. |
| 6 | Montar Consolidado | code | Junta os produtos de todos os fabricantes numa lista só, com as mesmas colunas e a coluna `Fabricante` depois de Produto. |
| 7 | Criar Planilha Consolidada | google_sheets (create) | "Giro de Estoque - Consolidado - <data>", com leitura para qualquer pessoa com o link. Segue mesmo se falhar. |
| 8 | Gravar Planilha Consolidada | google_sheets (append) | Grava todos os produtos na consolidada. Segue mesmo se falhar. |
| 9 | Resumo Consolidado | code | Resume o resultado (`ok`, `url`, `total`) para o e-mail. |
| 10 | Cada Fabricante | loop | Um fabricante por vez, com pausa de 3 s entre eles (o Google Sheets limita a cerca de 60 gravações por minuto); segue mesmo se um falhar. |
| 11 | Criar Planilha do Fabricante | google_sheets (create) | "Giro de Estoque - <fabricante> - <data>", com leitura para qualquer pessoa com o link. |
| 12 | Gravar Produtos na Planilha | google_sheets (append) | Produtos do fabricante (Código, Produto, Curva ABC, Status, Prioridade, Estoque Atual, Cobertura, Saída no Período, Saída/Dia, Sugestão de Compra). |
| 13 | Montar Linha do Índice | code | Linha `Fabricante`, `Produtos`, `Link`. |
| 14 | Registrar no Índice | google_sheets (append) | Grava a linha no índice. |
| 15 | Ler Índice | google_sheets (read) | Depois do loop, lê o índice (a saída `done` não devolve os links criados). |
| 16 | Montar E-mail | code | E-mail no padrão Waipe: destaque de ação imediata, indicadores, bloco "Planilha consolidada" com botão, ranking com botão e distribuição por status. Cruza os links do índice pelo nome ignorando espaços duplicados; fabricante sem planilha sai do ranking, gera um aviso no topo e entra em "Fabricantes com erro" no final. |
| 17 | Gmail: Enviar Email | gmail_send | Envia o relatório ao gestor. |

Fabricante sem nome no cadastro cai em "Sem fabricante". O ranking põe primeiro quem tem mais produtos em ação imediata
(ruptura ou compra urgente).

Status calculados (por cobertura e curva): Ruptura (gira e está zerado ou negativo), Comprar urgente, Comprar, Estoque
saudável, Excesso de estoque, Estoque parado (sem giro, com estoque) e Zerado sem giro.

## Como implantar em um cliente novo

1. Peça "quero criar o agente de giro de estoque": a skill `waipe-criar-agente` copia este modelo e faz as perguntas acima.
2. Crie o relatório do Data Lab com o texto abaixo e cole o ID no node Waipe Data.
3. Importe o JSON, conecte a conta Google (Sheets e Gmail) e ajuste o `CONFIG` dos nodes 3, 4 e 16.
4. Teste com o destinatário trocado por um e-mail interno, confira planilhas e links, restaure e ative.

## Configuração após importar

- **Google** (nodes 5, 7, 8, 11, 12, 14, 15 e 17): selecionar a conta Google conectada (a mesma para Sheets e Gmail).
- **Planilhas públicas**: as planilhas de fabricante, a consolidada e o índice ficam visíveis para quem tiver o link.
- **Relatório do Data Lab**: trocar `SUBSTITUA_PELO_ID_DO_RELATORIO`. Precisa trazer a coluna do fabricante.
- **Destinatário** (node 17): trocar `gestor@exemplo.com`.

### Relatório do Data Lab (texto para criar)

| Node | Texto do relatório |
|---|---|
| Waipe Data | `Liste todos os Produtos Ativos: Código do Produto, Nome do Produto, Fabricante do produto, Quantidade vendidos nos {ultimos_90_dias}, Quantidade de Estoque Atual.` |

`{ultimos_90_dias}` é parâmetro do Data Lab e precisa de valor padrão. Se tudo cair em "Sem fabricante", confira no log do
node Giro do Estoque o nome real das colunas e acrescente em `ALIASES_FABRICANTE`.

`CONFIG` do node **Giro do Estoque**:

| Constante | Valor | Para que serve |
|---|---|---|
| `PERIODO_DIAS` | 90 | Período coberto por `quantidade_vendida`. |
| `DIAS_PROJECAO_COMPRA` | 45 | Horizonte da sugestão de compra. |
| `ABC_CORTE_A` / `ABC_CORTE_B` | 0,80 / 0,95 | Cortes da curva ABC (volume acumulado). |
| `CAMPO_BASE_ABC` | quantidade_vendida | Base da curva ABC. |
| `ALIASES_FABRICANTE` / `TRECHOS_FABRICANTE` | fabricante, ... / fabric | Nomes aceitos da coluna do fabricante. |
| `FABRICANTE_VAZIO` | Sem fabricante | Texto para produto sem fabricante. |
| `TRATAR_NEGATIVO_COMO_ZERO` | false | Estoque negativo vira 0 na sugestão. |
| `COBERTURA_POR_CURVA` | A 10/20/90, B 7/15/150, C 5/10/180 | Dias de cobertura: crítico / atenção / excesso. |

`CONFIG` do node **Montar Fabricantes**: `ABA` ("Página1"), `COBERTURA_SEM_GIRO_TEXTO`, `COLUNAS` (campo e título de cada coluna da
planilha), `STATUS_ACAO` e `ORDEM_STATUS` (precisam bater com os textos do node Giro do Estoque). `CONFIG` do node **Montar Consolidado**: `COLUNA_FABRICANTE` (título da coluna do fabricante). `CONFIG` do node **Montar E-mail**:
`nomeEmpresa`, `nomeGestor`, `titulo`, `assunto`, `rotuloRelatorio`, `periodoDias`, `coresStatus`.

## Como testar

1. Importe `giro-estoque.json` no Waipe Flow e conecte a conta Google nos nodes de Sheets e no Gmail.
2. Troque o destinatário do node 17 por um e-mail de teste e execute.
3. Esperado: uma planilha por fabricante, a planilha consolidada, uma planilha-índice e um e-mail com destaque, ranking e um botão por fabricante. Confira no log do node 3 a coluna de fabricante usada e no log do node 16 "Fabricantes com planilha: N de N | com erro: 0".
4. Restaure o destinatário e ative.

## Histórico

### v1.4.0 (2026-10-29)
- Correção vinda do cliente piloto (`giro-estoque/v2.2.1`): com ~90 fabricantes o e-mail passava dos 102 KB e o Gmail
  cortava a mensagem (o modelo chegava a 232 KB). O ranking passa a usar `wpRanking`, função nova do kit que põe o estilo
  em classes no `<style>` do `wpPagina`: 61 KB com 90 fabricantes, 90 KB com 150.

### v1.3.0 (2026-10-29)
- Planilha consolidada vinda do cliente piloto (`giro-estoque/v2.2.0`): 4 nodes antes do loop (Montar Consolidado, Criar
  e Gravar Planilha Consolidada, Resumo Consolidado) geram uma planilha com todos os produtos e a coluna Fabricante. Os
  nodes de Sheets seguem mesmo se falharem. O e-mail ganha o bloco "Planilha consolidada" (kit Waipe) antes do ranking;
  se a planilha falhar, o bloco avisa e fica sem botão. Novo modelo de comunicação `planilhas/consolidado.html`.

### v1.2.0 (2026-10-29)
- Correção vinda do cliente piloto (`giro-estoque/v2.1.0`): fabricantes ficavam sem botão no e-mail quando o Google Sheets
  devolvia erro 429 (cota de gravações por minuto). O loop Cada Fabricante passa a ter pausa de 3 s entre fabricantes
  (a execução fica mais longa, ~6,75 s por fabricante).
- Montar E-mail: links do índice cruzados ignorando espaços duplicados no nome; fabricante sem planilha sai do ranking
  (numeração contínua), ganha aviso no topo (`wpAviso` alerta) e entra na seção "Fabricantes com erro". O node devolve
  também `fabricantes_com_erro`. Novo modelo de comunicação `consolidado-gestor-com-erro.html`.

### v1.1.0 (2026-10-22)
- E-mails no novo padrão de e-mail Waipe (claro, com modo escuro automático, desenho do Guardião da Amostra Padrão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `modelos/`, dentro da pasta do modelo, só com as peças enviadas, gerados rodando os nodes com dados fictícios.

### v1.0.0 (2026-10-22)
- Primeira versão do modelo no catálogo, anonimizada a partir de um agente em produção em um cliente, com o e-mail no padrão Waipe.
