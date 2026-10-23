---
nome: Produtos sem Giro - Inteligência de compras e estoque
slug: produtos-sem-giro
versao: 1.0.0
modelo_base: nenhum
gatilho: agendado (dias úteis, 07:00, America/Sao_Paulo)
icone: 📦
resumo: Cruza estoque e vendas do Data Lab das empresas do grupo e envia a planilha de produtos com 20 dias ou mais sem venda, mais o ranking dos mais vendidos com a cobertura de estoque.
frequencia: Segunda a sexta, 07:00
quem_recebe: Compras e gestão de estoque
atualizado: 2026-10-23
---

# Produtos sem Giro - Inteligência de compras e estoque

## Quando usar

Cliente que quer, todo dia útil, a lista dos **produtos parados** (20 dias ou mais sem venda) com o valor de estoque
empatado e, no mesmo disparo, o **ranking dos mais vendidos** com a cobertura de estoque, sinalizando o que precisa de
reposição. Funciona com uma ou várias empresas no grupo.

Modelos de comunicação (3 e-mails e a planilha): `.claude/waipe/catalogo/produtos-sem-giro/modelos/` (lista das peças em
`modelos.json`). Os e-mails seguem o **padrão de e-mail Waipe**.

Palavras-chave: estoque parado, produtos sem giro, sem venda, mais vendidos, cobertura, reposição, compras, planilha.

Parecido com `giro-estoque` (giro, cobertura e curva ABC por fabricante); este é diário e focado em produto parado e
reposição dos mais vendidos.

## Perguntas para personalizar

Pergunte ao usuário, nesta ordem (proponha o padrão entre parênteses):

1. **Nome da empresa** nos e-mails (`CONFIG.nomeEmpresa` dos três nodes "Montar E-mail ...").
2. **Quem recebe** os e-mails (campo `to` dos três nodes de Gmail; compras).
3. **Quando rodar** (dias úteis, 07:00).
4. **Dias sem venda** para entrar no alerta (`DIAS_MINIMOS`, 20) e **período do relatório de vendas** (`JANELA_DIAS`, 30).
5. **Giro por grupo ou por empresa** (`MODO_GIRO`, `'grupo'`: venda em qualquer empresa conta).
6. **Ranking dos mais vendidos**: quantos (`TOP_MAIS_VENDIDOS`, 30), ordem (`ORDENAR_POR`, faturamento) e cobertura mínima
   em dias (`COBERTURA_MINIMA`, 15).
7. **Códigos fora da análise**, como serviços (`CODIGOS_IGNORADOS`, padrão nenhum).

## Objetivo

Apontar todo dia útil os produtos parados há 20 dias ou mais nas empresas do grupo (com o valor de estoque empatado) e
mostrar o ranking dos mais vendidos com a cobertura de estoque, sinalizando o que precisa de reposição.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Dias úteis 7h | trigger_schedule | Dispara de segunda a sexta, 07:00 (`America/Sao_Paulo`). |
| 2 | Produtos em estoque | waipe_data | Relatório do Data Lab com o estoque e o custo por produto e empresa. |
| 3 | Vendas recentes | waipe_data | Relatório do Data Lab com as vendas do período (`JANELA_DIAS`). |
| 4 | Calcular produtos sem giro | code | Cruza estoque e vendas, calcula dias sem venda, cobertura e ranking e devolve as linhas da planilha e os dados dos e-mails. |
| 5 | Há produtos sem giro? | if | Segue para a planilha se `quantidade > 0`; senão, vai para o aviso. |
| 6 | Criar planilha | google_sheets (create) | Cria a planilha "Produtos sem giro - <data>". |
| 7 | Escrever cabeçalho | google_sheets (append) | Grava a linha de cabeçalho na aba `Página1`. |
| 8 | Gravar linhas | google_sheets (append) | Grava as linhas de `linhas` do node 4. |
| 9 | Consolidar gravação | merge_out | Junta as linhas gravadas em um item antes do e-mail. |
| 10 | Montar E-mail de Alerta | code | E-mail no padrão Waipe: produtos parados, valor empatado, resumo por empresa, lista e botão para a planilha. |
| 11 | Enviar alerta por e-mail | gmail_send | Envia o alerta. |
| 12 | Montar E-mail sem Produtos Parados | code | Ramo falso do node 5: aviso de que não há produto parado, com o resumo por empresa. |
| 13 | Avisar sem produtos parados | gmail_send | Envia o aviso. |
| 14 | Montar E-mail dos Mais Vendidos | code | Sai direto do node 4: ranking dos mais vendidos com a cobertura e o selo "Repor" ou "OK". |
| 15 | Enviar mais vendidos | gmail_send | Envia o ranking (sempre). |

O gatilho liga os nodes 2 e 3 em paralelo; o node 4 espera os dois. Do node 4 saem dois ramos: o do alerta (nodes 5 a
13) e o e-mail de mais vendidos (nodes 14 e 15), que é enviado sempre.

**Cobertura** = estoque do grupo / média diária de vendas na janela. Abaixo de `COBERTURA_MINIMA` (ou sem estoque), o
produto ganha o selo "Repor".

## Como implantar em um cliente novo

1. `waipe.py novo-agente <slug> --modelo produtos-sem-giro` e responda às perguntas acima.
2. Crie os dois relatórios do Data Lab com os textos abaixo e cole os IDs nos nodes 2 e 3.
3. Importe o JSON, conecte Google e Gmail e siga "Como testar".

## Configuração após importar

- **Credencial Google** (`credentialId` vazio): conectar nos três nodes de Google Sheets e nos três de Gmail.
- **Relatórios do Data Lab:** trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_ESTOQUE` e
  `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDAS_RECENTES` pelos IDs.
- **Agendamento:** dias úteis, 07:00. O flow entra inativo ao importar: ative depois do teste.

### Destinos

| Node | Campo | Teste | Produção |
|---|---|---|---|
| Enviar alerta por e-mail | `to` | e-mail interno de teste | compras (`compras@exemplo.com` no modelo) |
| Avisar sem produtos parados | `to` | e-mail interno de teste | compras |
| Enviar mais vendidos | `to` | e-mail interno de teste | compras |

### Relatórios do Data Lab (textos para criar)

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| Produtos em estoque | Produtos em estoque com custo | Liste todos os produtos com estoque, uma linha por produto e por empresa do grupo, com o código, a descrição, o grupo, o subgrupo, a quantidade em estoque, o custo médio e o custo de aquisição. |
| Vendas recentes | Vendas dos últimos 30 dias por item | Liste as vendas faturadas dos últimos 30 dias, uma linha por item vendido, com o código e a descrição do produto, a quantidade, o valor total da venda, o lucro, a data da venda (AAAA-MM-DD) e a empresa do grupo que vendeu. |

Colunas esperadas. Estoque: `codigo`, `nome`, `grupo`, `subgrupo`, `quantidade`, `custo_medio`, `custo_aquisicao`,
`_razaoOrigem`, `_cnpjOrigem`. Vendas: `produto`, `nomproduto`, `quantidade`, `total_venda`, `lucro`, `data_venda`,
`_razaoOrigem`, `_cnpjOrigem`. O período do relatório de vendas precisa bater com `JANELA_DIAS`.

### `CONFIG` de Calcular produtos sem giro

| Constante | Valor | Controla |
|---|---|---|
| `DIAS_MINIMOS` | `20` | Dias sem venda para o produto entrar no alerta. |
| `JANELA_DIAS` | `30` | Período coberto pelo relatório de vendas (30 ou 180). |
| `MODO_GIRO` | `'grupo'` | `'grupo'`: venda em qualquer empresa conta como giro. `'empresa'`: só a venda da própria empresa. |
| `FATOR_CUSTO_SUSPEITO` | `5` | Custo médio acima do custo de aquisição vezes este fator é tratado como inconsistente. |
| `MAX_LINHAS_EMAIL` | `50` | Máximo de produtos listados no e-mail de alerta (a planilha traz todos). |
| `TOP_MAIS_VENDIDOS` | `30` | Quantos produtos entram no e-mail de mais vendidos. |
| `ORDENAR_POR` | `'faturamento'` | Ordem do ranking: `'faturamento'` ou `'quantidade'`. |
| `COBERTURA_MINIMA` | `15` | Dias de estoque abaixo dos quais o produto é sinalizado para reposição. |
| `CODIGOS_IGNORADOS` | `[]` | Códigos fora da análise (ex.: serviços). |

### `CONFIG` dos nodes "Montar E-mail ..."

| Constante | Valor | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Empresa no topo do e-mail. |
| `rodape` | mensagem automática | Primeira linha do rodapé. |

## Atenção

- A planilha está com `sharing: anyone_reader`: qualquer pessoa com o link vê estoque e custo. Avalie `private`.
- Produto sem venda nenhuma na janela aparece como "Sem venda nos últimos N dias" (sem data da última venda).

## Como testar

1. Importe o JSON, conecte Google e Gmail e confira os dois relatórios do Data Lab.
2. Ponha um e-mail interno de teste nos três nodes de Gmail e rode manualmente pelo editor.
3. Esperado: uma planilha nova com os produtos parados há 20 dias ou mais e dois e-mails (alerta e mais vendidos), ou o
   aviso de que não há produtos parados mais o e-mail de mais vendidos.
4. Troque os destinatários para os de produção e ative o flow.

## Histórico

### v1.0.0 (2026-10-23)
- Adotado como modelo do agente do cliente piloto (anônimo) `produtos-sem-giro` v1.0.0, com os dados do cliente
  descaracterizados (destinos, IDs do Data Lab, códigos ignorados e exemplos).
- E-mails no padrão de e-mail Waipe, montados em três nodes "Montar E-mail ..."; o Calcular passa a devolver os dados dos
  e-mails. Travessão do título da planilha trocado por hífen. A planilha passa de `anyone_writer` a `anyone_reader`.
