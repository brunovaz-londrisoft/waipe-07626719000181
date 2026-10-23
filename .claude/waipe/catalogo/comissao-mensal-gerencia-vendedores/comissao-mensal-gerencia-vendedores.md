---
nome: Comissão Mensal - Gerência e Vendedores
slug: comissao-mensal-gerencia-vendedores
versao: 1.0.0
modelo_base: nenhum
gatilho: agendado (todo dia, 23:30, America/Sao_Paulo; só segue no último dia do mês)
icone: 💰
resumo: Fechamento mensal de comissões: ranking por vendedor para a gerência, e e-mail com planilha individual para cada vendedor.
frequencia: Último dia do mês, 23:30
quem_recebe: Gerência e cada vendedor com e-mail
atualizado: 2026-10-23
---

# Comissão Mensal - Gerência e Vendedores

## Quando usar

Cliente que paga **comissão por venda faturada** a partir de uma tabela de faixas por desconto: quanto maior o desconto
dado na venda, menor o percentual de comissão. No último dia do mês o agente calcula a comissão de cada venda com nota
fiscal emitida no mês, envia à **gerência** o ranking de vendedores com a planilha geral e envia a **cada vendedor** o
resumo da própria comissão com a planilha individual.

Modelos de comunicação (e-mail da gerência, e-mail do vendedor e planilhas): `.claude/waipe/catalogo/comissao-mensal-gerencia-vendedores/modelos/` (lista das peças em `modelos.json`). Os e-mails seguem o **padrão de e-mail Waipe**.

Palavras-chave: comissão, vendedores, fechamento do mês, nota fiscal, desconto, faixas, ranking, planilha por vendedor.

## Perguntas para personalizar

Pergunte ao usuário, nesta ordem (proponha o padrão entre parênteses):

1. **Nome da empresa** que aparece nos e-mails (`CONFIG.nomeEmpresa` dos dois nodes "Montar E-mail").
2. **E-mail da gerência** (destino do ranking, campo `to` de "Enviar Email Gerência").
3. **Tabela de comissão**: as faixas de desconto e o percentual de cada uma (`FAIXAS` de "Calcular Comissão") e o nome
   da tabela (`NOME_TABELA`, padrão "Tabela de Comissão").
4. **Base do desconto**: recalcular sobre o bruto (`RECALCULAR_DESCONTO: true`, padrão) ou usar o percentual do ERP.
5. **Quais operações não geram comissão** (prazos de bonificação, comodato, remessa, devolução, troca): vão no texto
   do relatório de vendas do Data Lab.
6. **Quem vê as planilhas**: leitura para quem tiver o link (padrão) ou privadas (`sharing` dos nodes "Criar Planilha").

## Objetivo

Calcular a comissão de cada venda **faturada no mês** (nota fiscal emitida no mês) pela tabela de faixas, enviar à
gerência o ranking de vendedores e a planilha geral, e enviar a cada vendedor a planilha individual com o resumo da
própria comissão.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Dispara todo dia, 23:30 (`America/Sao_Paulo`). |
| 2 | É o último dia do mês? | filter | Segue só quando amanhã é dia 1, ou seja, no último dia do mês. |
| 3 | Buscar Vendas | waipe_data | Relatório do Data Lab com as vendas faturadas no mês (texto em "Relatórios do Data Lab"). |
| 4 | Filtrar Vendas Faturadas no Mês | code | Mantém só as vendas com nota fiscal e data de emissão no mês corrente (referência `$today`). |
| 5 | Calcular Comissão | code | Calcula, venda a venda, o percentual de desconto sobre o bruto e o valor da comissão pela tabela de faixas. |
| 6 | Agregar Vendas | merge_out | Junta todas as vendas calculadas em um único item (`vendas`). |
| 7 | Buscar Vendedores | waipe_data | Relatório do Data Lab com o cadastro de vendedores (nome e e-mail). |
| 8 | Consolidar Comissões | code | Agrupa por vendedor, soma, monta o ranking (do maior para o menor vendido), as linhas das planilhas e a lista de vendedores com e-mail. |
| 9 | Criar Planilha Geral | google_sheets (create) | Cria "Comissões <mês/ano> - Todos os vendedores". |
| 10 | Expandir Linhas Gerais | code | Uma linha por venda, com as colunas na ordem fixa. |
| 11 | Gravar Planilha Geral | google_sheets (append) | Grava as linhas na aba `Página1` com `USER_ENTERED`. |
| 12 | Resumir Gravação Geral | merge_out | Junta as linhas gravadas antes do e-mail. |
| 13 | Montar E-mail da Gerência | code | E-mail no padrão Waipe: total de comissões, indicadores, ranking com barras, aviso de vendedores sem e-mail e botão para a planilha. |
| 14 | Enviar Email Gerência | gmail_send | Envia o ranking à gerência. |
| 15 | Um Vendedor por Vez | loop | Percorre `vendedores` (só quem tem e-mail no cadastro), um por vez; segue mesmo se um falhar. |
| 16 | Criar Planilha do Vendedor | google_sheets (create) | Cria "Comissão <mês/ano> - <vendedor>". |
| 17 | Linhas do Vendedor | code | Filtra as vendas do vendedor da iteração, com as colunas na ordem fixa. |
| 18 | Gravar Planilha do Vendedor | google_sheets (append) | Grava as linhas na aba `Página1` com `USER_ENTERED`. |
| 19 | Resumir Gravação do Vendedor | merge_out | Junta as linhas gravadas antes do e-mail. |
| 20 | Montar E-mail do Vendedor | code | E-mail no padrão Waipe com a comissão, o total vendido, as vendas do mês e o botão para a planilha individual. |
| 21 | Enviar Email ao Vendedor | gmail_send | Envia o resumo ao vendedor (`{{ $json.email }}`). |

**Quais vendas entram:** a comissão pertence ao mês de **emissão da nota fiscal**, não ao mês da data da venda. Uma
venda feita em 22/10 e faturada em 02/11 entra na comissão de novembro. Operações que não geram faturamento ficam de
fora no próprio Data Lab, mesmo com nota. Notas canceladas não entram.

**Regra da comissão:** a base é o valor líquido da venda (desconto abatido); a faixa é escolhida pelo percentual de
desconto **sobre o bruto** (líquido + desconto). Desconto indisponível dá comissão 0%; desconto negativo é tratado como 0%.
Faixas de exemplo (desconto até, inclusive): 0% = 5,0% | 5% = 4,8% | 10% = 4,5% | ... | 55% = 0,3% | acima de 55% = 0%.

**Planilhas** (geral e de cada vendedor), colunas nesta ordem: Lançamento, Nº da Nota, Data da Venda, Emissão da NF,
Nome do Cliente, Subtotal da Venda, Valor Total do Desconto, Valor Total da Venda, % do Desconto, Valor da Comissão,
Regra Aplicada, Nome do Vendedor, Nome da Empresa de Origem.

## Como implantar em um cliente novo

1. `waipe.py novo-agente <slug> --modelo comissao-mensal-gerencia-vendedores` e responda às perguntas acima.
2. Crie os dois relatórios do Data Lab com os textos abaixo e cole os IDs em "Buscar Vendas" e "Buscar Vendedores".
3. Ajuste `FAIXAS` e `NOME_TABELA` em "Calcular Comissão" e o `CONFIG` dos nodes "Montar E-mail".
4. Importe o JSON, conecte Google e Gmail e siga "Como testar".

## Configuração após importar

- **Credencial Google** (`credentialId` vazio): conectar nos 4 nodes de Google Sheets e nos 2 de Gmail.
- **Relatórios do Data Lab:** trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDAS_FATURADAS` e
  `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDEDORES` pelos IDs dos relatórios criados com os textos abaixo.
- **Localidade das planilhas:** as datas saem como `DD/MM/AAAA` e são gravadas com `USER_ENTERED`; a planilha precisa
  estar com localidade **Brasil** (Arquivo → Configurações → Localidade).

### Destinos

| Node | Campo | Teste | Produção |
|---|---|---|---|
| Enviar Email Gerência | `to` | e-mail interno de teste | e-mail da gerência (`gerencia@exemplo.com` no modelo) |
| Enviar Email ao Vendedor | `to` | e-mail interno de teste, fixo no campo | `{{ $json.email }}` (e-mail do vendedor vindo do cadastro) |

### Relatórios do Data Lab (textos para criar)

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| Buscar Vendas | Vendas faturadas no mês | Texto abaixo. O parâmetro `{este_mes}` é o mês corrente. |
| Buscar Vendedores | Cadastro de vendedores | Liste todos os vendedores ativos com nome (`nomvendedor`) e e-mail (`email`). |

Texto do relatório de **Buscar Vendas**:

```
Liste todas as vendas que possuam **nota fiscal emitida** (campo `NUMNOTA` preenchido) cuja **data de emissão da nota fiscal** esteja em **{este_mes}**, independentemente da data da venda, exibindo os seguintes campos:

- Lançamento
- Número da Nota Fiscal (`NUMNOTA`)
- Data de Emissão da Nota Fiscal (formato AAAA-MM-DD)
- Nome do Cliente
- Código do Vendedor
- Nome do Vendedor
- Subtotal da Venda
- Valor Total da Venda
- Valor Total de Desconto
- Percentual de Desconto
- Data da Venda (formato AAAA-MM-DD)
- Prazo de pagamento

A data de emissão deve vir da tabela de notas fiscais, relacionada à venda pelo número da nota. **Desconsidere notas fiscais canceladas.**

**Cálculo do percentual de desconto:**

Percentual de Desconto = (Valor Total de Desconto / Subtotal da Venda) × 100.

Apresente todos os valores monetários com 4 casas decimais e o percentual de desconto com 4 casas decimais.

**Desconsidere as vendas que possuam os seguintes códigos na coluna `prazo` do banco de dados:** <códigos de prazo de bonificação, comodato, remessa, devolução, troca e demais operações sem faturamento do cliente>.

Ordene pela data de emissão da nota fiscal, da mais recente para a mais antiga. Não agrupe lançamentos diferentes nem invente dados ausentes.
```

Colunas esperadas: `lancamento`, `numnota`, `data_emissao_nota`, `nomcliente`, `codigo_vendedor`, `nomvendedor`,
`subtotal_venda`, `total_venda`, `desconto_total`, `percentual_desconto`, `data_venda`, `prazo`, `_razaoOrigem`.
Do cadastro de vendedores: `nomvendedor` (ou `nome`) e `email`. O vendedor sem e-mail no cadastro aparece num aviso no
e-mail da gerência e não recebe o individual.

### `CONFIG` de Calcular Comissão

| Constante | Valor | Controla |
|---|---|---|
| `NOME_TABELA` | `Tabela de Comissão` | Nome da tabela gravado em cada venda. |
| `RECALCULAR_DESCONTO` | `true` | `true` recalcula o desconto sobre o bruto (líquido + `desconto_total`); `false` usa o `percentual_desconto` da origem. |
| `FAIXAS` | 21 faixas | Limite de desconto (`ate`, inclusive) e percentual de comissão. |

### `CONFIG` dos nodes Montar E-mail

| Constante | Valor | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Empresa no topo e no rodapé dos e-mails. |
| `titulo` (gerência) | `Comissões do mês por vendedor` | Título do e-mail da gerência. |
| `assunto` | `Comissões de {mes} - ranking de vendedores` / `Sua comissão de {mes}` | Assunto; `{mes}` vira o mês de referência. |
| `rodape` | mensagem automática | Primeira linha do rodapé. |

### Outros nodes de código

- **Filtrar Vendas Faturadas no Mês:** `CAMPOS_DATA` lista só datas de emissão da nota e `CAMPOS_NOTA` os nomes aceitos
  para o número da nota. Aceita `AAAA-MM-DD`, `DD/MM/AAAA` e timestamp.
- **Consolidar Comissões:** `CAMPOS_NOME` e `CAMPOS_EMAIL` definem como ler o cadastro de vendedores.
- **Expandir Linhas Gerais** e **Linhas do Vendedor:** `COLUNAS` define a ordem das colunas. O Google Sheets ordena os
  cabeçalhos em ordem alfabética; cada cabeçalho recebe um prefixo invisível (`​`) que força a ordem sem mudar o
  texto visível.

## Atenção

- As planilhas estão com `sharing: anyone_reader`: qualquer pessoa com o link lê valores de vendas e comissões, e a geral
  mostra a comissão de todos. Avalie `private`.
- Rodar às 23:30 do último dia garante que as notas do dia entrem no fechamento do mês.
- Uma nota cancelada e reemitida em outro mês pode gerar comissão nos dois meses; venda devolvida depois de comissionada
  não gera estorno.
- O limite de saída do node de código é de cerca de 1 MiB; com muitas vendas, confira o log do Consolidar.

## Como testar

1. Importe o JSON no Waipe Flow, conecte Google e Gmail e confira os dois relatórios do Data Lab.
2. Ponha um e-mail interno de teste nos dois nodes de Gmail.
3. Rode manualmente pelo editor a partir de "Buscar Vendas" (o filtro só deixa passar no último dia do mês).
4. Esperado: uma planilha geral com as vendas faturadas no mês, o e-mail da gerência com ranking e totais e, por vendedor
   com e-mail, uma planilha individual e um e-mail com a comissão.
5. Confira o log de Filtrar Vendas Faturadas no Mês e de Consolidar Comissões e as datas como data na planilha.
6. Troque os destinos para produção e ative o flow.

## Histórico

### v1.0.0 (2026-10-23)
- Adotado como modelo do agente do cliente piloto (anônimo) `comissao-mensal-gerencia-vendedores` v1.0.0, com os dados
  do cliente descaracterizados.
- Corrigidos os problemas do flow de origem: o loop dos vendedores passa a receber o Consolidar, a planilha individual
  grava com `USER_ENTERED` e o filtro do último dia do mês fica ligado a um agendamento diário às 23:30.
- E-mails no padrão de e-mail Waipe, montados nos nodes "Montar E-mail da Gerência" e "Montar E-mail do Vendedor"; o
  Consolidar passa a devolver o ranking em dados (`ranking_resumo`, `sem_email`).
