---
nome: Olho no Estoque
slug: olho_estoque
versao: 2.1.0
plataforma: 2.1.0
categoria: Produtos
dependencias: nenhuma
modelo_base: nenhum
atualizado: 2026-11-19
---

# Olho no Estoque

## Quando usar

Quem precisa repor antes de faltar sem ter o estoque mínimo cadastrado: o mínimo é projetado pela venda real de cada
produto, e a página mostra também o dinheiro parado. Palavras-chave: estoque, reposição, mínimo, vai faltar, parado,
dinheiro parado, grupo de produto.

## Objetivo

Todo dia, o que vai faltar (zerado ou poucos dias de venda), o que está abaixo do mínimo projetado, com a quantidade
para repor, e o que está parado ocupando dinheiro, por grupo. Não usa o mínimo cadastrado no Gestor.

## Relatório do Data Lab

Nome sugerido: **Olho no Estoque**. Texto para criar:

```
liste todos os Produtos Ativos:
Código do Produto,
Nome do Produto,
Grupo do Produto,
Quantidade de Estoque Total,
Custo Unitário,
Quantidade vendida nos {ultimos_90_dias},
Data da Última Venda.
```

| Coluna do relatório | Campo no plugin | Obrigatória | Observação |
|---|---|---|---|
| `codigo` | `codigo` | sim | chave |
| `nome` | `nome` | não | sem nome, usa o código |
| `grupo_nome` | `grupo` | não | vazio vira "Sem grupo" |
| `estoque_total` | `estoque` | sim | loja + almoxarifado |
| `custo_unitario` | `custo` | não | valor em estoque e dinheiro parado |
| `qtd_vendida_periodo` | `vendido` | sim | o período precisa ser igual ao "Período das vendas" |
| `data_ultima_venda` | `ultima_venda` | não | sem ela, parado = sem venda no período |

## Como calcula

1. Venda por dia = vendido ÷ período. Dias de venda = estoque ÷ venda por dia.
2. Mínimo projetado = venda por dia × "Mínimo e reposição para" (30 dias), arredondado para cima.
3. Sugestão de reposição = mínimo projetado − estoque (só em Vai faltar e Repor).

| Situação | Regra |
|---|---|
| 🔴 Vai faltar | vende e o estoque dura até "Vai faltar com até" (7) dias, ou zerado com venda |
| 🟠 Repor | estoque igual ou abaixo do mínimo projetado |
| 💤 Parado | tem estoque e não vende há "Parado sem venda há" (365) dias |
| ⚪ Sem venda no período | não vendeu no período e não é parado |
| 🟢 OK | o resto |

## Banco

Ao instalar, o Waipe Páginas cria o schema `olho_estoque` com as tabelas padrão (cargas, histórico, configuração, integração) e a
tabela `olho_estoque.produtos`, uma linha por item (chave + empresa) e uma coluna por campo:

| Campo | Tipo |
|---|---|
| `codigo` | texto |
| `nome` | texto |
| `grupo` | texto |
| `estoque` | numero |
| `custo` | numero |
| `vendido` | numero |
| `ultima_venda` | data |
| `minimo` | inteiro |
| `saida_dia` | numero |
| `cobertura_dias` | inteiro |
| `dias_sem_venda` | inteiro |
| `sugestao` | inteiro |
| `valor_estoque` | numero |
| `situacao` | texto |

Índices: (grupo), (situacao). Migrações explícitas: nenhuma (coluna nova entra sozinha ao atualizar).

## Telas

- **Indicadores**: vai faltar, repor, parados, dinheiro parado (R$), sem venda no período, valor em estoque (R$);
  situação do estoque, repor agora (top 15), grupos com mais para repor e com mais dinheiro parado. Imprimir.
- **Produtos**: filtros grupo e situação; ordem por situação.
- **Por grupo**: grupos com mais para repor primeiro.
- **Detalhe**: produto, mínimo projetado, sugestão e histórico.

## Configurações

| Parâmetro | Padrão | O que muda |
|---|---|---|
| Período das vendas | 90 dias | divisor da venda por dia (trava: só muda depois de mudar o Data Lab) |
| Vai faltar com até | 7 dias de venda | situação Vai faltar (menor que o mínimo) |
| Parado sem venda há | 365 dias | situação Parado |
| Mínimo e reposição para | 30 dias de venda | mínimo projetado e sugestão |
| Texto para produto sem grupo | Sem grupo | agrupamento |
| Produtos ignorados | vazio | serviços e mão de obra cadastrados como produto |

## Perguntas para personalizar

1. Qual estoque usar: total, só loja ou só almoxarifado?
2. Para quantos dias de venda repor e com quantos dias avisar que vai faltar?
3. Há produtos que não devem entrar (serviço, mão de obra)?

## Como instalar e testar

1. Waipe Páginas > Configurações gerais > Páginas > Instalar página (.json): `olho_estoque.json`.
2. Na página, Configurações > Integração: crie o relatório no Data Lab com o texto acima, cole o ID, baixe e importe
   os dois flows, ative e cole a URL do webhook.
3. Atualizar agora; confira um produto de giro conhecido (venda por dia, mínimo projetado e sugestão).
4. `exemplo.json` traz linhas fictícias no formato do Data Lab.

## Dependências

Nenhuma além dos flows da integração: o flow agendado (todo dia às 07:00) e o Atualizar pelo Painel, gerados
pela própria página em Configurações > Integração, buscam o relatório **Olho no Estoque** no Data Lab e
enviam as linhas para a página. Nenhum agente do repositório é necessário.

## Histórico

### v2.1.0 (2026-11-19)
- Seções `integracao` (passos e horário 07:00 do flow agendado) e `exportar` (Excel, CSV e Imprimir) no plugin (Waipe Páginas 2.1.0).

### v2.0.0 (2026-11-19)
- Seção `banco`: a instalação cria a tabela da página com uma coluna por campo (Waipe Páginas 2.0.0).

### v1.0.0 (2026-11-19)
- Primeira versão como plugin (antes era código dentro do Waipe Páginas; mínimo projetado pela venda).
