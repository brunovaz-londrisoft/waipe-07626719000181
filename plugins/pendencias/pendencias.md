---
nome: Pendências de Ontem
slug: pendencias
versao: 2.1.0
plataforma: 2.1.0
categoria: Rotina
modelo_base: nenhum
atualizado: 2026-11-19
---

# Pendências de Ontem

## Quando usar

Dono ou gestor que começa o dia querendo saber o que ficou em aberto até ontem: vendas não faturadas, O.S. abertas,
orçamentos não finalizados e contas a receber e a pagar vencidas. Palavras-chave: pendências, rotina da manhã,
orçamentos, não faturadas, O.S., contas vencidas.

## Objetivo

Uma lista única e diária do que ficou pendente, com destaque para o que é de ontem e o que está atrasado, por tipo e
por cliente. Não envia nada. Limite: o Gestor não tem controle de entrega (só aparece se estiver amarrada a venda ou O.S.).

## Relatório do Data Lab

Nome sugerido: **Pendências de Ontem**. Texto para criar:

```
liste as pendências em aberto, uma linha por documento, juntando:
1) Vendas com status VENDA sem nota fiscal emitida e Orçamentos de venda não finalizados dos {ultimos_90_dias};
2) Ordens de Serviço sem nota fiscal emitida e Orçamentos de O.S. não finalizados dos {ultimos_90_dias};
3) Contas a Receber em aberto (com saldo) com vencimento até hoje;
4) Contas a Pagar em aberto (sem pagamento) com vencimento até hoje.
Colunas:
Tipo (Venda, Orçamento de Venda, O.S., Orçamento de O.S., Conta a Receber ou Conta a Pagar),
Número do Documento,
Data do Documento,
Data de Vencimento,
Cliente ou Fornecedor,
Vendedor,
Valor.
```

| Coluna do relatório | Campo no plugin | Obrigatória | Observação |
|---|---|---|---|
| `tipo` | `tipo` | sim | define o grupo pelos trechos aceitos |
| `numero_documento` | `documento` | sim | chave = grupo + documento |
| `data_documento` | `data` | uma das datas | vendas, O.S. e orçamentos |
| `data_vencimento` | `vencimento` | uma das datas | contas |
| `cliente_fornecedor` | `pessoa` | não | vazio vira "(sem nome)" |
| `vendedor` | `vendedor` | não | |
| `valor` | `valor` | não | |

## Como calcula

1. Grupo pelo Tipo (trechos editáveis, nesta ordem): conta a receber, conta a pagar, orçamento de O.S., O.S. (só o
   tipo inteiro "os"), orçamento de venda, venda; o resto vai para Outros.
2. Descarta: documento vazio, clientes em "Ignorar sempre" e, só em vendas e O.S., clientes em "Vendas e O.S. sem nota
   de propósito" (contratos com nota de serviço mensal).
3. Data de referência: vencimento nas contas, data do documento no resto. Dias em aberto até hoje; data futura sai.

| Situação | Regra |
|---|---|
| 🔴 Atrasado | mais dias que "Atrasada depois de" (7) |
| 🟠 De ontem | 1 dia |
| 🟡 Recente | 2 até o limite |
| 🔵 De hoje | 0 dia |
| ⚪ Sem data | sem data no relatório |

## Banco

Ao instalar, o Waipe Páginas cria o schema `pendencias` com as tabelas padrão (cargas, histórico, configuração, integração) e a
tabela `pendencias.pendencias`, uma linha por item (chave + empresa) e uma coluna por campo:

| Campo | Tipo |
|---|---|
| `tipo` | texto |
| `documento` | texto |
| `data` | data |
| `vencimento` | data |
| `pessoa` | texto |
| `vendedor` | texto |
| `valor` | numero |
| `grupo` | texto |
| `referencia` | data |
| `dias` | inteiro |
| `situacao` | texto |

Índices: (pessoa), (situacao). Migrações explícitas: nenhuma (coluna nova entra sozinha ao atualizar).

## Telas

- **Indicadores**: pendências, de ontem, atrasadas, vendas não faturadas, O.S. em aberto, contas a receber vencidas;
  situação, "Ficou de ontem" (top 15), por tipo. Imprimir.
- **Lista de pendências**: filtros Tipo, Situação e Cliente; filtro de período 📅 pela data; ordem por dias em aberto, do menor para o maior.
- **Por cliente**: quem tem mais pendências de ontem e atrasadas primeiro.
- **Detalhe**: documento e histórico.

## Configurações

| Parâmetro | Padrão | O que muda |
|---|---|---|
| Atrasada depois de | 7 dias | situação Atrasado |
| Vendas e O.S. sem nota de propósito | vazio | clientes de contrato fora das vendas/O.S. |
| Ignorar sempre | CONSUMIDOR FINAL | quem fica fora |
| Trechos por grupo | receber, pagar, orçamento de O.S., os, orçamento, venda/pedido | grupo de cada linha |

## Perguntas para personalizar

1. Há clientes de contrato cujas vendas ficam sem nota de propósito (prefeitura, autarquia, condomínio)?
2. O cliente lança contas a pagar no sistema? Se não, tirar o item 4 do texto do Data Lab.
3. Até quantos dias para trás olhar vendas e O.S. (`{ultimos_90_dias}`)?
4. Quantos dias para considerar atrasado?

## Como instalar e testar

1. Waipe Páginas > Configurações gerais > Páginas > Instalar página (.json): `pendencias.json`.
2. Na página, Configurações > Integração: crie o relatório no Data Lab com o texto acima, cole o ID, baixe e importe
   os dois flows, ative e cole a URL do webhook.
3. Atualizar agora; confira em Configurações > Colunas que todas as colunas aparecem com ✓ e que "De ontem" bate com o sistema.
4. `exemplo.json` traz linhas fictícias no formato do Data Lab.

## Histórico

### v2.1.0 (2026-11-19)
- Seções `integracao` (passos e horário 07:00 do flow agendado) e `exportar` (Excel, CSV e Imprimir) no plugin (Waipe Páginas 2.1.0).

### v2.0.0 (2026-11-19)
- Seção `banco`: a instalação cria a tabela da página com uma coluna por campo (Waipe Páginas 2.0.0).

### v1.0.0 (2026-11-19)
- Primeira versão como plugin (antes era código dentro do Waipe Páginas; regras iguais).
