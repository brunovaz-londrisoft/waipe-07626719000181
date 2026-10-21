---
nome: Pendências de Ontem
slug: pendencias-de-ontem
versao: 0.0.0
modelo_base: nenhum
gatilho: agendado (todos os dias, 08:00, America/Sao_Paulo)
atualizado: 2026-10-20
---

# Pendências de Ontem

## Objetivo

Todo dia às 08:00, consulta quatro relatórios do Data Lab e manda um e-mail em HTML com o que ficou pendente até
ontem: orçamentos de venda e de O.S. não finalizados, vendas e O.S. não faturadas, e contas a pagar e a receber em
aberto (vencidas até ontem e vencendo hoje). No topo, oito totalizadores; abaixo, a lista de cada um.

Origem (fala da cliente no diagnóstico de 25/08/2026): "gosto de começar sabendo o que ficou pendente de ontem: que
entrega não foi feita, que pedido eu não faturei, que resposta fiquei de dar pro cliente".

**Limite combinado com a cliente:** o Gestor não tem controle de entrega. Entrega amarrada a uma venda ou O.S. aparece
por ali; status de entrega ou rota, não.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Diário (`scheduleType: "daily"`), 08:00, `America/Sao_Paulo`. |
| 2 | Vendas da Semana | waipe_data (`data_lab`) | Vendas e orçamentos de venda do período, com status e nota fiscal. |
| 3 | O.S. da Semana | waipe_data (`data_lab`) | O.S. e orçamentos de O.S. do período, com status e nota fiscal. |
| 4 | Contas a Pagar da Semana | waipe_data (`data_lab`) | Contas a pagar em aberto com vencimento no período. |
| 5 | Contas a Receber da Semana | waipe_data (`data_lab`) | Contas a receber em aberto com vencimento no período. |
| 6 | Montar E-mail de Pendências | code (`all_items`) | Lê cada relatório por `$node["<nome do node>"]`, abre o envelope do Data Lab, classifica as linhas nos oito grupos (regras abaixo), soma quantidade e valor e monta o HTML. Devolve `{ assunto, html, email, hoje, totais, avisos }`. |
| 7 | Enviar E-mail de Pendências | gmail_send | `bodyType: "html"`, `subject: {{ $json.assunto }}`, `body: {{ $json.html }}`, `to` conforme "Destinos". |

Topologia: o Agendamento abre quatro ramos (nodes 2 a 5), que convergem no node 6 (merge do motor: ele executa uma
vez, depois dos quatro). O node 6 não usa a ordem dos itens recebidos: pega cada relatório pelo nome do node, então
**não renomeie os nodes 2 a 5** sem ajustar `CONFIG.nodes`.

O e-mail sai **todo dia**, mesmo sem pendência (cartões zerados com "Nada pendente"). Não há node de filtro.

**Formato do retorno do Data Lab** (visto no teste de 20/10/2026): cada node devolve um item
`{ dados: [ { dados: [linhas], empresasComErro, empresasConsultadas, erros, totalRegistros } ] }`. O node 6 abre esse
envelope e, se vier algo em `erros` ou se um relatório não for encontrado, mostra um aviso amarelo no topo do e-mail.
O log (console) do node mostra quantas linhas e quais colunas vieram de cada relatório.

### Os oito grupos

"Hoje" é a data de `$now` ajustada pelo fuso (`CONFIG.fusoHoras` = -3); "até ontem" é qualquer data anterior a hoje.

| # | Totalizador | Relatório | Regra |
|---|---|---|---|
| 1 | Orçamentos de venda | Vendas da Semana | `status` = ORÇAMENTO e `data` antes de hoje. |
| 2 | Vendas não faturadas | Vendas da Semana | `status` = VENDA, `tem_nf` = NÃO (ou `nf_numero` vazio) e `data` antes de hoje. |
| 3 | Orçamentos de O.S. | O.S. da Semana | `status` = ORÇAMENTO e `data` antes de hoje. |
| 4 | O.S. não faturadas | O.S. da Semana | `status` = VENDA (é assim que o relatório de O.S. devolve a O.S.), `tem_nf` = NÃO e `data` antes de hoje. |
| 5 | A pagar vencidas | Contas a Pagar da Semana | `datavencimento` antes de hoje, `datapagamento` vazia ou `1900-01-01`, `remanescente` > 0. |
| 6 | A receber vencidas | Contas a Receber da Semana | `datavencimento` antes de hoje, `saldo` > 0. |
| 7 | A pagar hoje | Contas a Pagar da Semana | `datavencimento` = hoje, mesmas regras do 5. |
| 8 | A receber hoje | Contas a Receber da Semana | `datavencimento` = hoje, `saldo` > 0. |

Vendas e O.S. lançadas hoje ficam fora. Linhas vazias, clientes de `nomesIgnorados` e (só nos grupos 2 e 4) clientes de
`clientesNaoFaturados` são descartados.

### E-mail

Assunto: `Pendências até ontem - Manduca Piscinas - 21/10/2026`.

Padrão visual dos e-mails Waipe já em produção (o do Guardião da Amostra Padrão), com os ajustes aprovados em
20/10/2026 e sem nenhum dado de outro cliente: fundo `#F3F4F6`, marca Waipe no topo (ícone "W" em imagem de
`CONFIG.logoUrl` + a palavra "waipe" em texto ao lado, com link para waipe.com.br; sem URL, só o texto) e empresa com "Relatório diário · data" à direita, cartão
branco com borda `#E5E7EB`, raio 8 px e faixa `#303030` de 4 px no topo, sobretítulo dourado ("Rotina da manhã"),
título de 28 px, fonte Inter (com Arial de reserva), texto secundário `#4B5563`, layout em tabelas, versão para
celular (colunas secundárias somem abaixo de 620 px) e modo escuro (fundos `#111827` / `#1F2937` / `#27303F`, bordas
`#374151`, logo invertido).

1. **Saudação**: "Bom dia, Tais. Este é o resumo do que ficou em aberto até ontem e do que vence hoje...".
2. **Aviso** (só se houver erro de relatório): faixa amarela com o problema.
3. **Totalizadores**, em dois blocos de 2 × 2 cartões, cada um com quantidade, nome e valor total:

   | Vendas e O.S. até ontem | |
   |---|---|
   | Orçamentos de venda | Orçamentos de O.S. |
   | Vendas não faturadas | O.S. não faturadas |

   | Financeiro em aberto | |
   |---|---|
   | A pagar vencidas | A receber vencidas |
   | A pagar hoje | A receber hoje |

   Cores: verde-oliva (`#F1F2EC` / `#5A6344`) quando há pendência, vermelho suave (`#FEF2F2` / `#B42828`) nas vencidas
   com pendência, cinza (`#F9FAFB`) com "Nada pendente" quando zerado.
4. **Listas**, uma por grupo, na ordem dos totalizadores, com título "Nome (quantidade)" e a descrição à direita:

   | Grupo | Colunas | Ordem |
   |---|---|---|
   | Orçamentos de venda / de O.S. | Nº, Data, Cliente (+ "lançado há X dias"), Vendedor, Valor | data mais antiga primeiro |
   | Vendas / O.S. não faturadas | Nº, Data, Cliente (+ "lançada há X dias"), Vendedor, Valor | data mais antiga primeiro |
   | A pagar / a receber vencidas | Fornecedor ou Cliente (+ "venceu há X dias"), Lançamento · parcela, Venc., Valor | vencimento mais antigo primeiro |
   | A pagar / a receber hoje | Fornecedor ou Cliente, Lançamento · parcela, Valor | maior valor primeiro |

   Cada lista mostra no máximo `CONFIG.maxItensPorLista` linhas e fecha com "e mais N (R$ X)". Grupo vazio mostra
   "✓ Nada pendente.".
5. **Rodapé**: "Enviado automaticamente pelo Waipe todos os dias às 08:00 para Manduca Piscinas." e "Londrisoft ·
   Londrina, PR · Brasil".

## ⚠️ Pontos a validar

1. **Destinatário.** O `to` está com `SUBSTITUA_PELO_EMAIL_DE_TESTE` e o `CONFIG.email` com
   `SUBSTITUA_PELO_EMAIL_DESTINO`. Falta o e-mail que recebe.
2. **"Até ontem" limitado pelo `{inicio_semana}`.** Os quatro relatórios começam em `{inicio_semana}`; o que for de
   antes disso não entra. Como o flow roda todo dia, na segunda às 08:00 (com `{inicio_semana}` = segunda) os grupos
   1 a 6 vêm vazios. Recomendação: valor padrão de `{inicio_semana}` mais antigo (ex.: 30 ou 90 dias atrás).
3. **Muitas vendas não faturadas.** No teste de 19 e 20/10, a maioria das vendas veio com `tem_nf` = NÃO, inclusive balcão
   (cliente "CLIENTE", código 100). Confirmar com a Tais se toda venda não faturada é mesmo pendência; se não, usar
   `nomesIgnorados` (ex.: "CLIENTE") ou `clientesNaoFaturados` (ex.: CMTU, prefeitura).
4. **O.S. não faturadas porque a NFS-e sai fora do Gestor.** Hoje ela emite nota de serviço no emissor nacional. Enquanto a
   NFS-e não for configurada no Gestor, toda O.S. entra em "O.S. não faturadas".
5. **Contas a pagar quase vazias.** Ela ainda não lança contas a pagar no sistema (no teste veio só UNIMED).
6. **CNPJ.** Os relatórios estão lendo o CNPJ 07626719000181 (`_razaoOrigem` = "IVAN ALEX MANDUCA", a razão social
   antiga). Conferir se é a base certa depois que a arquitetura dos dois CNPJ for decidida.
7. **Texto dos relatórios de vendas e O.S.** O "l" sobrando em "até {hoje}l" já foi tirado do texto aqui; falta tirar
   também no Data Lab. O de vendas ainda tem um espaço duplo em "do  {inicio_semana}".
8. **Logo.** `CONFIG.logoUrl` precisa ser uma URL **pública** do **ícone "W" em PNG** (quadrado; o Gmail não mostra SVG
   em `<img>` nem arquivo local). A palavra "waipe" é texto, então aparece mesmo com imagens bloqueadas. Enquanto
   estiver com `SUBSTITUA_PELA_URL_PUBLICA_DO_LOGO_PNG`, o topo mostra só o texto.
9. **Tamanho do HTML.** Uma expressão tem teto de 256 KB. Com 8 listas de até 20 linhas o e-mail fica bem abaixo disso;
   se `maxItensPorLista` for muito aumentado, o envio pode falhar com `ExpressionResultTooLarge`.

## Configuração após importar

- **Conector Waipe / Data Lab**: os quatro nodes já vêm com os IDs dos relatórios (tabela abaixo). Em outro ambiente,
  recriar os relatórios com os textos e trocar os IDs.
- **Credencial Google** (`google_oauth2`): conectar no node Enviar E-mail de Pendências (no JSON: `credentialId: ""`).
- **Destinatário**: ver "Destinos".
- **Agendamento**: o flow entra inativo ao importar; ativar depois do teste.

### Relatórios do Data Lab (textos para criar)

Textos registrados exatamente como foram criados no Data Lab em 2026-10-20.

| Node | ID no Data Lab | Texto do relatório |
|---|---|---|
| Vendas da Semana | `cmvh26l57001uqi2n37tgybge` | `Liste todos os registros da tabela de vendas do  {inicio_semana} até {hoje}, incluindo tanto os que estão com status de venda quanto os que estão com status de orçamento, e tanto os que têm nota fiscal quanto os que não têm. Não considere registros cancelados. Colunas: número da venda ou orçamento (numero), data de lançamento (data), status do registro indicando se é VENDA ou ORÇAMENTO (status), situação do registro (situacao), código do cliente (codcliente), nome do cliente (cliente), nome do vendedor (vendedor), valor total (valor), indicador se a venda tem nota fiscal emitida, SIM ou NÃO (tem_nf), número da nota fiscal (nf_numero). Quando a venda não tiver nota fiscal, deixe os campos da nota vazios. Ordene pela data de lançamento, da mais antiga para a mais recente.` |
| O.S. da Semana | `cmvh37n64001wqi2nw1l5tfhp` | `Liste todos os registros da tabela de Ordem de Serviço do {inicio_semana} até {hoje}, incluindo tanto os que estão com status de OS quanto os que estão com status de orçamento, e tanto os que têm nota fiscal quanto os que não têm. Não considere registros cancelados. Colunas: número da venda ou orçamento (numero), data de lançamento (data), status do registro indicando se é VENDA ou ORÇAMENTO (status), situação do registro (situacao), código do cliente (codcliente), nome do cliente (cliente), nome do vendedor (vendedor), valor total (valor), indicador se a venda tem nota fiscal emitida, SIM ou NÃO (tem_nf), número da nota fiscal (nf_numero). Quando a venda não tiver nota fiscal, deixe os campos da nota vazios. Ordene pela data de lançamento, da mais antiga para a mais recente.` |
| Contas a Pagar da Semana | `cmvh3tvxs0020qi2nd9p8173r` | `Liste todos os contas a pagar em aberto com o vencimento do {inicio_semana} até {hoje}.` |
| Contas a Receber da Semana | `cmvh3n3tn001yqi2nxc3r9efz` | `Liste todos os contas a receber em aberto com o vencimento do {inicio_semana} até {hoje}.` |

`{inicio_semana}` e `{hoje}` são parâmetros do Data Lab e precisam de valor padrão (ver ponto 2).

**Colunas que cada relatório devolve** (teste de 20/10/2026; todos trazem também `_cnpjOrigem` e `_razaoOrigem`):

| Relatório | Colunas | Usadas pelo flow |
|---|---|---|
| Vendas da Semana | `numero`, `data`, `status` (VENDA / ORÇAMENTO), `situacao`, `codcliente`, `cliente`, `vendedor`, `valor`, `tem_nf` (SIM / NÃO), `nf_numero` | `numero`, `data`, `status`, `cliente`, `vendedor`, `valor`, `tem_nf`, `nf_numero` |
| O.S. da Semana | as mesmas + `nomstatus` (veio vazio); `status` = VENDA para a O.S. e ORÇAMENTO para o orçamento; `data` com hora | as mesmas das vendas |
| Contas a Pagar da Semana | `lancamento`, `parcela`, `fornecedor` (código), `nomfornece`, `descricao`, `datavencimento`, `datapagamento` (`1900-01-01` = sem pagamento), `valor`, `valor_pago`, `remanescente` | `lancamento`, `parcela`, `nomfornece`, `datavencimento`, `datapagamento`, `remanescente` |
| Contas a Receber da Semana | `lancamento`, `parcela`, `cliente` (código), `nomcliente`, `descricao`, `banco`, `categoria`, `dataemissao`, `datavencimento`, `valor`, `valorbase`, `valorpago`, `saldo` | `lancamento`, `parcela`, `nomcliente`, `datavencimento`, `saldo` |

### `CONFIG` de Montar E-mail de Pendências

| Constante | Valor | Controla |
|---|---|---|
| `nomeEmpresa` | `Manduca Piscinas` | Nome no topo, no rodapé e no assunto. |
| `nomeDestinatario` | `Tais` | Nome na saudação. |
| `logoUrl` | `SUBSTITUA_PELA_URL_PUBLICA_DO_LOGO_PNG` | Ícone "W" do topo (PNG público quadrado, exibido em 28 × 28 px, invertido no modo escuro). Com o placeholder, mostra só a palavra "waipe". |
| `email` | `SUBSTITUA_PELO_EMAIL_DESTINO` | Destinatário real devolvido em `email` (usado na produção). |
| `titulo` | `Pendências até ontem` | Título do e-mail. |
| `assunto` | `Pendências até ontem - Manduca Piscinas` | Assunto; o node acrescenta " - dd/mm/aaaa". |
| `fusoHoras` | `-3` | Fuso usado para saber qual é "hoje" a partir de `$now` (UTC). |
| `maxItensPorLista` | `20` | Linhas por lista antes do "e mais N" (ver ponto 8). |
| `nomesIgnorados` | `["CONSUMIDOR FINAL"]` | Clientes/fornecedores descartados em todos os grupos (nome exato, sem diferenciar maiúsculas). |
| `clientesNaoFaturados` | `[]` | Clientes cuja venda ou O.S. fica sem faturar de propósito: fora dos grupos 2 e 4. Comparação por "contém". |
| `statusOrcamento` | `["ORCAMENTO", "ORÇAMENTO"]` | Valores de `status` tratados como orçamento. |
| `statusVenda` | `["VENDA"]` | Valores de `status` tratados como venda no relatório de vendas. |
| `statusOS` | `["OS", "O.S.", "ORDEM DE SERVICO", "ORDEM DE SERVIÇO", "VENDA"]` | Valores de `status` tratados como O.S. no relatório de O.S. |
| `nodes` | nomes dos nodes 2 a 5 | De onde o node lê cada relatório. |
| `aliases` | colunas da tabela acima | Nomes de coluna aceitos para cada campo (o primeiro preenchido vale). |

### Destinos

| Node | Campo | Teste | Produção |
|---|---|---|---|
| Enviar E-mail de Pendências | `to` | `bruno.vaz@londrisoft.londrina.br` (modo `fixed`, provisório até a validação) | `{{ $json.email }}` (modo `expression`) |

## Como testar

1. Importar `pendencias-de-ontem.json` no Waipe Flow (Dashboard → Importar JSON) e conectar a conta Google.
2. Trocar `SUBSTITUA_PELO_EMAIL_DE_TESTE` pelo seu e-mail e rodar pelo editor.
3. No log do node Montar E-mail de Pendências, conferir as linhas e colunas de cada relatório.
4. Esperado: oito totalizadores com quantidade e valor e as oito listas. Conferir que nada lançado hoje entra nos grupos
   de vendas e O.S. e que "hoje" só traz vencimento de hoje. Abrir também no celular e no modo escuro.
5. Resultado do teste local com os dados de 19 e 20/10 (simulando a execução em 21/10): 3 orçamentos de venda,
   3 vendas não faturadas, 1 orçamento de O.S., 1 O.S. não faturadas, 1 a pagar vencida, 2 a receber vencidas, 1 a receber hoje
   (amostra reduzida das linhas reais).
6. Preencher o destinatário de produção e ativar.

## Histórico

### Não publicado
- JSON atualizado com o export do Waipe Flow de 21/10/2026: envio de teste para o Bruno (`to` fixo) até a validação; depois troca para o e-mail da cliente.
- Tirado o "l" sobrando em "até {hoje}l" nos textos dos relatórios Vendas da Semana e O.S. da Semana.
- Primeira versão da documentação, a partir da passagem de bastão de 27/08/2026.
- Envio trocado de WhatsApp (Z-API) para e-mail (Gmail, HTML).
- Relatório "Pedidos em Aberto" trocado por "Vendas da Semana" (vendas e orçamentos com status e dados da NF):
  orçamento = não finalizado em venda; venda com `tem_nf` = NÃO = não faturada.
- Texto do relatório Vendas da Semana atualizado para a versão criada no Data Lab (parâmetros `{inicio_semana}` e
  `{hoje}`, só `tem_nf` e `nf_numero` da nota).
- Relatório "O.S. em Aberto" trocado por "O.S. da Semana" (O.S. e orçamentos de O.S. com status e NF, texto criado no
  Data Lab): orçamento de O.S. = não aprovado; O.S. com `tem_nf` = NÃO = não faturada.
- Relatório "Títulos Vencidos" trocado por dois: "Contas a Receber da Semana" e "Contas a Pagar da Semana" (em aberto,
  vencimento de `{inicio_semana}` até `{hoje}`), separados em vencidas e vencendo hoje.
- Fluxo redefinido: todos os dias às 08:00, e-mail sempre enviado (sem filtro), com oito totalizadores (até ontem e
  vencendo hoje) e uma lista por grupo abaixo.
- Primeiro JSON do flow, a partir do esqueleto montado no Waipe Flow (IDs reais dos quatro relatórios), com as colunas
  reais devolvidas pelo Data Lab e o HTML no padrão visual dos e-mails Waipe.
- Visual do e-mail ajustado conforme o HTML aprovado: fonte Inter, logo em imagem (`CONFIG.logoUrl`), raio 8 px, cinzas
  e vermelho novos e paleta do modo escuro.
- Vendas e O.S. sem faturamento passam a ser chamadas de "não faturadas" em todo o e-mail, no código e na documentação
  (constante `clientesNaoFaturados`; nos totais, `vendaNaoFaturada` e `osNaoFaturada`).
- Marca do topo refeita como ícone "W" em imagem + "waipe" em texto, igual ao modelo aprovado.
