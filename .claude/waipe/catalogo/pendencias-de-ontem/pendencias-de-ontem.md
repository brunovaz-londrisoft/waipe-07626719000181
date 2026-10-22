---
nome: Pendências de Ontem
slug: pendencias-de-ontem
versao: 1.1.0
modelo_base: nenhum
gatilho: agendado (todos os dias, 08:00, America/Sao_Paulo)
icone: 🗂️
resumo: E-mail com o que ficou pendente até ontem (orçamentos, vendas e O.S. não faturadas, contas vencidas) e o que vence hoje.
frequencia: Todos os dias, 08:00
quem_recebe: Responsável pela rotina da manhã
nota: Este fluxo envia um único e-mail por dia, sem mensagens a vendedores.
atualizado: 2026-10-22
---

# Pendências de Ontem

## Quando usar

Cliente (dono ou gestor financeiro e comercial) que quer **começar o dia sabendo o que ficou pendente**: orçamentos de venda
e de O.S. não finalizados, vendas e O.S. não faturadas, e contas a pagar e a receber vencidas ou vencendo hoje. Sai um e-mail
por dia, mesmo sem pendência.

Palavras-chave: pendências, rotina da manhã, orçamentos, não faturadas, contas a pagar, contas a receber, vencidas, O.S.

Modelo de comunicação (e-mail diário): `.claude/waipe/catalogo/pendencias-de-ontem/modelos/` (lista das peças em `modelos.json`).

## Perguntas para personalizar

1. **Nome da empresa** e **nome de quem recebe**, e o **e-mail de destino**.
2. **Horário** (padrão: todos os dias, 08:00) e se roda também no fim de semana.
3. O cliente **lança contas a pagar** no sistema? E emite nota de serviço fora do Gestor (a O.S. nunca fica "faturada")?
4. **Clientes que não faturam de propósito** (balcão, prefeitura) e nomes a ignorar.
5. **Até quantos dias para trás** o relatório olha (valor padrão do parâmetro `{inicio_semana}`; sugestão: 30 a 90 dias).
6. Quantas linhas por lista (padrão: 20).

## Objetivo

Todo dia, consulta quatro relatórios do Data Lab e manda um e-mail com o que ficou pendente até ontem: orçamentos de venda e de
O.S. não finalizados, vendas e O.S. não faturadas, e contas a pagar e a receber em aberto (vencidas até ontem e vencendo hoje).
No topo, o destaque com o total de pendências e os totalizadores por grupo; abaixo, a lista de cada um.

**Limite:** o Gestor não tem controle de entrega. Entrega amarrada a uma venda ou O.S. aparece por ali; status de entrega ou rota, não.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Diário, 08:00, `America/Sao_Paulo`. |
| 2 | Vendas da Semana | waipe_data | Vendas e orçamentos de venda do período, com status e nota fiscal. |
| 3 | O.S. da Semana | waipe_data | O.S. e orçamentos de O.S. do período, com status e nota fiscal. |
| 4 | Contas a Pagar da Semana | waipe_data | Contas a pagar em aberto com vencimento no período. |
| 5 | Contas a Receber da Semana | waipe_data | Contas a receber em aberto com vencimento no período. |
| 6 | Montar E-mail de Pendências | code | Lê cada relatório pelo nome do node, classifica as linhas nos oito grupos, soma quantidade e valor e monta o e-mail no padrão Waipe. |
| 7 | Enviar E-mail de Pendências | gmail_send | HTML, assunto `{{ $json.assunto }}`, corpo `{{ $json.html }}`, destinatário `{{ $json.email }}`. |

O Agendamento abre quatro ramos que convergem no node 6 (ele executa uma vez, depois dos quatro). O node 6 pega cada relatório
pelo nome do node, então **não renomeie os nodes 2 a 5** sem ajustar `CONFIG.nodes`. Se um relatório vier com `erros` ou não for
encontrado, o e-mail mostra um aviso no topo. O log do node mostra quantas linhas e quais colunas vieram de cada relatório.

### Os oito grupos

"Hoje" é a data de `$now` ajustada pelo fuso (`CONFIG.fusoHoras`); "até ontem" é qualquer data anterior a hoje.

| # | Totalizador | Relatório | Regra |
|---|---|---|---|
| 1 | Orçamentos de venda | Vendas da Semana | `status` = ORÇAMENTO e `data` antes de hoje. |
| 2 | Vendas não faturadas | Vendas da Semana | `status` = VENDA, `tem_nf` = NÃO (ou `nf_numero` vazio) e `data` antes de hoje. |
| 3 | Orçamentos de O.S. | O.S. da Semana | `status` = ORÇAMENTO e `data` antes de hoje. |
| 4 | O.S. não faturadas | O.S. da Semana | `status` = VENDA (é assim que o relatório devolve a O.S.), `tem_nf` = NÃO e `data` antes de hoje. |
| 5 | A pagar vencidas | Contas a Pagar da Semana | `datavencimento` antes de hoje, `datapagamento` vazia ou `1900-01-01`, `remanescente` > 0. |
| 6 | A receber vencidas | Contas a Receber da Semana | `datavencimento` antes de hoje, `saldo` > 0. |
| 7 | A pagar hoje | Contas a Pagar da Semana | `datavencimento` = hoje, mesmas regras do 5. |
| 8 | A receber hoje | Contas a Receber da Semana | `datavencimento` = hoje, `saldo` > 0. |

Vendas e O.S. lançadas hoje ficam fora. Linhas vazias, clientes de `nomesIgnorados` e (só nos grupos 2 e 4) clientes de
`clientesNaoFaturados` são descartados. Cada lista mostra no máximo `CONFIG.maxItensPorLista` linhas e fecha com "e mais N (R$ X)".

## Como implantar em um cliente novo

1. Peça "quero criar o agente de pendências": a skill `waipe-criar-agente` copia este modelo e faz as perguntas acima.
2. Crie os quatro relatórios do Data Lab com os textos abaixo, defina o valor padrão de `{inicio_semana}` e de `{hoje}` e cole os IDs nos nodes 2 a 5.
3. Importe o JSON, conecte a conta Google no Gmail e ajuste o `CONFIG` do node 6.
4. Teste com o `to` fixo de um e-mail interno, confira os totais e as listas (celular e modo escuro), volte para `{{ $json.email }}` e ative.

## Configuração após importar

- **Relatórios do Data Lab**: trocar os quatro `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_...` pelos IDs criados.
- **Credencial Google** (`google_oauth2`): conectar no node Enviar E-mail de Pendências.
- **Destinatário**: `CONFIG.email` (o node de envio usa `{{ $json.email }}`).
- **Agendamento**: o flow entra inativo; ative depois do teste.

### Relatórios do Data Lab (textos para criar)

| Node | Texto do relatório |
|---|---|
| Vendas da Semana | `Liste todos os registros da tabela de vendas do {inicio_semana} até {hoje}, incluindo tanto os que estão com status de venda quanto os que estão com status de orçamento, e tanto os que têm nota fiscal quanto os que não têm. Não considere registros cancelados. Colunas: número da venda ou orçamento (numero), data de lançamento (data), status do registro indicando se é VENDA ou ORÇAMENTO (status), situação do registro (situacao), código do cliente (codcliente), nome do cliente (cliente), nome do vendedor (vendedor), valor total (valor), indicador se a venda tem nota fiscal emitida, SIM ou NÃO (tem_nf), número da nota fiscal (nf_numero). Quando a venda não tiver nota fiscal, deixe os campos da nota vazios. Ordene pela data de lançamento, da mais antiga para a mais recente.` |
| O.S. da Semana | `Liste todos os registros da tabela de Ordem de Serviço do {inicio_semana} até {hoje}, incluindo tanto os que estão com status de OS quanto os que estão com status de orçamento, e tanto os que têm nota fiscal quanto os que não têm. Não considere registros cancelados. Colunas: número da venda ou orçamento (numero), data de lançamento (data), status do registro indicando se é VENDA ou ORÇAMENTO (status), situação do registro (situacao), código do cliente (codcliente), nome do cliente (cliente), nome do vendedor (vendedor), valor total (valor), indicador se a venda tem nota fiscal emitida, SIM ou NÃO (tem_nf), número da nota fiscal (nf_numero). Quando a venda não tiver nota fiscal, deixe os campos da nota vazios. Ordene pela data de lançamento, da mais antiga para a mais recente.` |
| Contas a Pagar da Semana | `Liste todos os contas a pagar em aberto com o vencimento do {inicio_semana} até {hoje}.` |
| Contas a Receber da Semana | `Liste todos os contas a receber em aberto com o vencimento do {inicio_semana} até {hoje}.` |

`{inicio_semana}` e `{hoje}` são parâmetros do Data Lab e precisam de valor padrão.

**Colunas que cada relatório devolve** (todas trazem também `_cnpjOrigem` e `_razaoOrigem`):

| Relatório | Colunas | Usadas pelo flow |
|---|---|---|
| Vendas da Semana | `numero`, `data`, `status`, `situacao`, `codcliente`, `cliente`, `vendedor`, `valor`, `tem_nf`, `nf_numero` | `numero`, `data`, `status`, `cliente`, `vendedor`, `valor`, `tem_nf`, `nf_numero` |
| O.S. da Semana | as mesmas; `status` = VENDA para a O.S. e ORÇAMENTO para o orçamento | as mesmas das vendas |
| Contas a Pagar da Semana | `lancamento`, `parcela`, `fornecedor`, `nomfornece`, `descricao`, `datavencimento`, `datapagamento`, `valor`, `valor_pago`, `remanescente` | `lancamento`, `parcela`, `nomfornece`, `datavencimento`, `datapagamento`, `remanescente` |
| Contas a Receber da Semana | `lancamento`, `parcela`, `cliente`, `nomcliente`, `descricao`, `banco`, `categoria`, `dataemissao`, `datavencimento`, `valor`, `valorbase`, `valorpago`, `saldo` | `lancamento`, `parcela`, `nomcliente`, `datavencimento`, `saldo` |

`CONFIG` de **Montar E-mail de Pendências**:

| Constante | Valor no modelo | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Nome no topo, no rodapé e no assunto. |
| `nomeDestinatario` | `Nome do Responsável` | Nome na saudação. |
| `email` | `destinatario@exemplo.com` | Destinatário devolvido em `email`. |
| `titulo` | `Pendências até ontem` | Título do destaque. |
| `assunto` | `Pendências até ontem - NOME DA EMPRESA` | Assunto; o node acrescenta " - dd/mm/aaaa". |
| `fusoHoras` | `-3` | Fuso para saber qual é "hoje" a partir de `$now` (UTC). |
| `maxItensPorLista` | `20` | Linhas por lista antes do "e mais N". |
| `nomesIgnorados` | `["CONSUMIDOR FINAL"]` | Clientes e fornecedores descartados em todos os grupos. |
| `clientesNaoFaturados` | `[]` | Clientes cuja venda ou O.S. fica sem faturar de propósito (fora dos grupos 2 e 4). |
| `statusOrcamento`, `statusVenda`, `statusOS` | ver node | Valores de `status` tratados como orçamento, venda e O.S. |
| `nodes` | nomes dos nodes 2 a 5 | De onde o node lê cada relatório. |
| `aliases` | colunas da tabela acima | Nomes de coluna aceitos para cada campo. |

## Cuidados

- **"Até ontem" é limitado pelo `{inicio_semana}`:** o que for de antes não entra. Use um valor padrão mais antigo (30 a 90 dias).
- **Muitas vendas não faturadas:** vendas de balcão costumam vir sem nota. Confirme com quem recebe se toda venda não faturada é pendência; se não, use `nomesIgnorados` ou `clientesNaoFaturados`.
- **O.S. não faturadas** quando a nota de serviço sai fora do Gestor: toda O.S. entra no grupo 4 enquanto a NFS-e não for configurada no Gestor.
- **Contas a pagar quase vazias** se o cliente ainda não lança contas a pagar no sistema.
- **Tamanho do HTML:** uma expressão tem teto de 256 KB. Com 8 listas de até 20 linhas o e-mail fica bem abaixo; aumentar muito `maxItensPorLista` pode falhar com `ExpressionResultTooLarge`.

## Como testar

1. Importe `pendencias-de-ontem.json` no Waipe Flow e conecte a conta Google.
2. Troque o `to` do node de envio por um e-mail de teste (modo fixo) e rode pelo editor.
3. No log do node 6, confira as linhas e colunas de cada relatório.
4. Esperado: destaque com o total, oito totalizadores e as oito listas. Nada lançado hoje entra nos grupos de vendas e O.S., e "hoje" só traz vencimento de hoje. Abra também no celular e no modo escuro.
5. Volte o `to` para `{{ $json.email }}`, preencha `CONFIG.email` e ative.

## Histórico

### v1.1.0 (2026-10-22)
- E-mails no novo padrão de e-mail Waipe (claro, com modo escuro automático, desenho do Guardião da Amostra Padrão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `modelos/`, dentro da pasta do modelo, só com as peças enviadas, gerados rodando os nodes com dados fictícios.

### v1.0.0 (2026-10-22)
- Primeira versão do modelo no catálogo, anonimizada a partir de um agente em produção em um cliente, com o e-mail no padrão Waipe.
