---
nome: CMV Mensal - Inteligência de compras e estoque
slug: cmv-mensal
versao: 1.0.0
modelo_base: nenhum
gatilho: webhook (POST com o período; sem período, mês anterior)
icone: 🧮
resumo: Calcula o CMV, as vendas, o lucro e a margem por mês, empresa e produto a partir das vendas do Data Lab, grava a planilha e envia o resumo por e-mail.
frequencia: Sob demanda (chamada do webhook)
quem_recebe: Diretoria e compras
atualizado: 2026-10-23
---

# CMV Mensal - Inteligência de compras e estoque

## Quando usar

Cliente que quer saber o **custo das mercadorias vendidas** (CMV) de um mês ou de um período, com vendas, lucro bruto e
margem por empresa do grupo, por mês e por produto, usando o custo gravado em cada venda no Gestor. Quem chama o webhook
escolhe o período; sem período, o agente calcula o mês anterior completo. O resultado vai numa planilha nova, num e-mail
de resumo e na resposta do webhook (JSON).

Modelos de comunicação (e-mail e planilha): `.claude/waipe/catalogo/cmv-mensal/modelos/` (lista das peças em
`modelos.json`). O e-mail segue o **padrão de e-mail Waipe**.

Palavras-chave: CMV, custo da mercadoria vendida, margem bruta, lucro bruto, fechamento do mês, compras, webhook, planilha.

## Perguntas para personalizar

Pergunte ao usuário, nesta ordem (proponha o padrão entre parênteses):

1. **Nome da empresa** no e-mail (`CONFIG.nomeEmpresa` de "Montar E-mail do CMV").
2. **Quem recebe** o resumo (campo `to` de "Enviar CMV por e-mail"; diretoria).
3. **Como disparar**: chamada do webhook por outro sistema ou agendamento (troque o gatilho por um `trigger_schedule`
   chamado `Receber período` para rodar todo dia 1 com o mês anterior).
4. **Códigos fora da análise**, como serviços (`CODIGOS_IGNORADOS`, padrão nenhum).
5. **Quantos produtos** com maior CMV aparecem no e-mail (`MAX_PRODUTOS_EMAIL`, 20).

## Objetivo

Mostrar o CMV das empresas do grupo no período, com vendas, lucro bruto e margem por mês, por empresa e por produto,
usando o custo registrado em cada venda. O resultado vai numa planilha do Google Sheets, num e-mail de resumo e na
resposta do webhook.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Receber período | trigger_webhook | `POST` com o período no corpo; responde pelos nodes de resposta (`by_node`). |
| 2 | Vendas 6 meses | waipe_data | Relatório do Data Lab com as linhas de venda dos últimos 6 meses (com custo). |
| 3 | Calcular CMV | code | Define o período, filtra as vendas, soma venda e CMV por mês, empresa e produto e devolve as linhas da planilha, os dados do e-mail (`email`) e a resposta em JSON. |
| 4 | Há vendas no período? | if | Segue para a planilha se `quantidade > 0`; senão, vai para Responder sem vendas. |
| 5 | Criar planilha CMV | google_sheets (create) | Cria a planilha "CMV <início> a <fim>". |
| 6 | Escrever cabeçalho CMV | google_sheets (append) | Grava o cabeçalho na aba `Página1`. |
| 7 | Gravar linhas CMV | google_sheets (append) | Grava as linhas de `linhas` do node 3. |
| 8 | Consolidar gravação CMV | merge_out | Junta as linhas gravadas em um item antes do e-mail. |
| 9 | Montar E-mail do CMV | code | E-mail no padrão Waipe: CMV do período, vendas, lucro, margem, resumo por empresa e por mês, maiores CMVs, avisos e botão para a planilha. |
| 10 | Enviar CMV por e-mail | gmail_send | Envia o resumo. |
| 11 | Responder com CMV | webhook_respond | Devolve o resultado em JSON com o link da planilha. |
| 12 | Responder sem vendas | webhook_respond | Ramo falso do node 4: devolve a resposta (ou o erro de período) em JSON. |

**Período (corpo do `POST`):**

```json
{ "mes": "2026-09" }
```

ou `{"data_inicial": "2026-09-01", "data_final": "2026-09-30"}`. Também aceita `MM/AAAA` e `DD/MM/AAAA`. Sem corpo,
usa o **mês anterior completo**. O período precisa caber nos 6 meses do relatório do Data Lab.

**Regras do cálculo:** CMV = `total_custo` da venda (ou quantidade x `custo_unitario`). Venda sem custo entra com CMV
zero e é avisada no e-mail. Devoluções (quantidade negativa) não são descontadas, só contadas no aviso. A planilha traz,
por mês e empresa, uma linha por produto, o subtotal da empresa, o subtotal do mês e, no fim, o total do período.

## Como implantar em um cliente novo

1. `waipe.py novo-agente <slug> --modelo cmv-mensal` e responda às perguntas acima.
2. Crie o relatório do Data Lab com o texto abaixo e cole o ID em "Vendas 6 meses".
3. Importe o JSON, conecte Google e Gmail e siga "Como testar".

## Configuração após importar

- **Credencial Google** (`credentialId` vazio): conectar nos três nodes de Google Sheets e no Gmail.
- **Relatório do Data Lab:** trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDAS_COM_CUSTO` pelo ID do relatório.
- **Webhook:** depois de importar, copie a URL do node "Receber período" para quem vai chamar o agente.

### Destinos

| Node | Campo | Teste | Produção |
|---|---|---|---|
| Enviar CMV por e-mail | `to` | e-mail interno de teste | diretoria (`diretoria@exemplo.com` no modelo) |

### Relatórios do Data Lab (textos para criar)

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| Vendas 6 meses | Vendas com custo (6 meses) | Liste todas as vendas faturadas dos últimos 6 meses, uma linha por item vendido, com a data da venda (AAAA-MM-DD), o código e a descrição do produto, o grupo e o subgrupo, a quantidade, o valor total da venda, o custo total do item (ou o custo unitário na venda) e a empresa do grupo que vendeu. |

Colunas esperadas: `data_venda`, `produto`, `nomproduto`, `grupo`, `subgrupo`, `quantidade`, `total_venda`,
`total_custo` (ou `custo_unitario`) e a empresa de origem (`_razaoOrigem`, `_cnpjOrigem`).

### `CONFIG` de Calcular CMV

| Constante | Valor | Controla |
|---|---|---|
| `CODIGOS_IGNORADOS` | `[]` | Códigos de produto fora da análise (ex.: serviços). |
| `MAX_PRODUTOS_EMAIL` | `20` | Quantos produtos com maior CMV aparecem no e-mail. |
| `MAX_BYTES_DETALHE` | `900000` | Acima deste tamanho a planilha recebe só os subtotais mensais, sem o detalhe por produto. |

### `CONFIG` de Montar E-mail do CMV

| Constante | Valor | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Empresa no topo do e-mail. |
| `rodape` | mensagem automática | Primeira linha do rodapé. |

## Atenção

- A planilha está com `sharing: anyone_reader`: qualquer pessoa com o link vê vendas, custo e margem. Avalie `private`.
- O webhook está sem autenticação (`authType: none`): não divulgue a URL ou ative uma autenticação no node.
- Se o relatório cobrir menos de 6 meses, períodos mais antigos voltam sem vendas.

## Como testar

1. Importe o JSON, conecte Google e Gmail e confira o relatório do Data Lab.
2. Ponha um e-mail interno de teste no node de Gmail e chame o webhook (ou rode pelo editor) com `{"mes": "AAAA-MM"}`
   de um mês fechado.
3. Esperado: uma planilha "CMV 01/MM/AAAA a DD/MM/AAAA", o e-mail com o CMV, vendas, lucro e margem e a resposta em JSON
   com o link da planilha. Sem vendas no período, só a resposta "sem vendas".
4. Troque o destinatário para o de produção.

## Histórico

### v1.0.0 (2026-10-23)
- Adotado como modelo do agente do cliente piloto (anônimo) `cmv-mensal` v1.0.0, com os dados do cliente
  descaracterizados (destinos, ID do Data Lab, códigos ignorados e exemplos).
- Gatilho trocado de manual para o webhook "Receber período" que o cálculo já esperava, com resposta pelos nodes
  `webhook_respond`.
- E-mail no padrão de e-mail Waipe, montado no node "Montar E-mail do CMV"; o Calcular CMV passa a devolver os dados do
  e-mail (`email`). Margem com vírgula em todo o e-mail. A planilha passa de `anyone_writer` a `anyone_reader`.
