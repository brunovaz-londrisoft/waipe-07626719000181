---
nome: Cobrança em Aberto
slug: cobranca
versao: 2.1.0
plataforma: 2.1.0
categoria: Financeiro
modelo_base: nenhum
atualizado: 2026-11-19
---

# Cobrança em Aberto

## Quando usar

Quem cuida do financeiro e quer saber quem cobrar primeiro: títulos vencidos e não pagos por cliente e por tempo de
atraso, sem disparar nada ao cliente. Palavras-chave: cobrança, boleto, contas a receber, inadimplência, atraso, vencidos.

## Objetivo

Uma lista de cobrança decidida pela pessoa (nada é enviado ao cliente), com o crítico primeiro, os títulos muito
antigos separados para revisar (podem ter sido pagos e não baixados) e os clientes com regra própria fora do alerta.

## Relatório do Data Lab

Nome sugerido: **Cobrança em Aberto**. Texto para criar:

```
liste todas as Contas a Receber em aberto (com saldo maior que zero), vencidas ou a vencer nos próximos 7 dias:
Número do Título,
Parcela,
Código do Cliente,
Nome do Cliente,
Data de Emissão,
Data de Vencimento,
Valor do Título,
Saldo em Aberto,
Forma de Pagamento.
```

| Coluna do relatório | Campo no plugin | Obrigatória | Observação |
|---|---|---|---|
| `lancamento` | `titulo` | sim | chave = título/parcela |
| `parcela` | `parcela` | não | |
| `cliente` | `codigo_cliente` | não | fica vazio se for a mesma coluna do nome |
| `nomcliente` | `cliente` | não | vazio vira "(sem nome)" |
| `dataemissao` | `emissao` | não | |
| `datavencimento` | `vencimento` | sim | |
| `valor_titulo` | `valor` | saldo ou valor | |
| `saldo_em_aberto` | `saldo` | saldo ou valor | sem a coluna, usa o valor; saldo zero sai |
| `forma_pagamento` | `forma` | não | |

## Como calcula

Dias de atraso = hoje − vencimento.

| Situação | Regra |
|---|---|
| 🟢 A vencer | vence hoje ou depois |
| ⚪ Regra própria do cliente | vencido de cliente em "Clientes com regra própria" |
| ⚫ Revisar (muito antigo) | mais de "Revisar depois de" (365) dias |
| 🔴 Crítico | mais de "Crítico depois de" (30) dias |
| 🟡 Vencido | de 1 até o limite crítico |

A cobrar = crítico + vencido (sem revisar e regra própria). Clientes em "Ignorar sempre" ficam fora.

## Banco

Ao instalar, o Waipe Páginas cria o schema `cobranca` com as tabelas padrão (cargas, histórico, configuração, integração) e a
tabela `cobranca.titulos`, uma linha por item (chave + empresa) e uma coluna por campo:

| Campo | Tipo |
|---|---|
| `titulo` | texto |
| `parcela` | texto |
| `codigo_cliente` | texto |
| `cliente` | texto |
| `emissao` | data |
| `vencimento` | data |
| `valor` | numero |
| `saldo` | numero |
| `forma` | texto |
| `dias_atraso` | inteiro |
| `situacao` | texto |

Índices: (cliente), (situacao). Migrações explícitas: nenhuma (coluna nova entra sozinha ao atualizar).

## Telas

- **Indicadores**: a cobrar (R$), títulos e clientes a cobrar, acima do limite crítico (R$), para revisar, a vencer
  (R$); quem cobrar primeiro (top 12), tempo de atraso em faixas, maiores saldos, situação dos títulos. Imprimir.
- **Títulos**: código e nome do cliente, título e parcela separados; filtro de período 📅 por vencimento ou emissão;
  ordem por dias de atraso, do menor para o maior.
- **Por cliente**: título mais antigo primeiro, depois o maior saldo.
- **Detalhe**: título e histórico.

## Configurações

| Parâmetro | Padrão | O que muda |
|---|---|---|
| Crítico depois de | 30 dias | situação Crítico |
| Revisar depois de | 365 dias | situação Revisar (precisa ser maior que o crítico) |
| Clientes com regra própria de pagamento | vazio | situação Regra própria |
| Ignorar sempre | vazio | quem fica fora |

## Perguntas para personalizar

1. Algum cliente paga fora do prazo por regra (prefeitura, órgão público)?
2. Quantos dias para crítico e para revisar?
3. A remessa e o retorno bancário estão ativos? Sem eles, a baixa não é confiável e a lista mostra títulos já pagos.

## Como instalar e testar

1. Waipe Páginas > Configurações gerais > Páginas > Instalar página (.json): `cobranca.json`.
2. Na página, Configurações > Integração: crie o relatório no Data Lab com o texto acima, cole o ID, baixe e importe
   os dois flows, ative e cole a URL do webhook.
3. Atualizar agora; confira um título conhecido no detalhe (vencimento, atraso, saldo).
4. `exemplo.json` traz linhas fictícias no formato do Data Lab.

## Histórico

### v2.1.0 (2026-11-19)
- Seções `integracao` (passos e horário 07:00 do flow agendado) e `exportar` (Excel, CSV e Imprimir) no plugin (Waipe Páginas 2.1.0).

### v2.0.0 (2026-11-19)
- Seção `banco`: a instalação cria a tabela da página com uma coluna por campo (Waipe Páginas 2.0.0).

### v1.0.0 (2026-11-19)
- Primeira versão como plugin (antes era código dentro do Waipe Páginas; regras iguais).
