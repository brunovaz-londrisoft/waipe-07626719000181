---
nome: Giro de Estoque
slug: giro
versao: 2.1.0
plataforma: 2.1.0
categoria: Produtos
modelo_base: nenhum
atualizado: 2026-11-19
---

# Giro de Estoque

## Quando usar

Gestor ou comprador que quer saber o que comprar e o que está parado: giro, cobertura em dias, curva ABC e sugestão
de compra de cada produto, por fabricante. Palavras-chave: estoque, giro, cobertura, curva ABC, ruptura, compra,
sugestão de compra, fabricante, estoque parado.

## Objetivo

Mostrar todo dia, produto a produto, quanto tempo o estoque dura no ritmo de venda, o que está em ruptura ou precisa
de compra e o que está parado, com a sugestão de quanto comprar. Não faz pedido de compra nem envia nada.

## Relatório do Data Lab

Nome sugerido: **Giro de Estoque**. Texto para criar:

```
liste todos os Produtos Ativos:
Código do Produto,
Nome do Produto,
Fabricante do Produto,
Quantidade vendidos nos {ultimos_90_dias},
Quantidade de Estoque Atual.
```

| Coluna do relatório | Campo no plugin | Obrigatória | Observação |
|---|---|---|---|
| código | `codigo` | sim | chave do item |
| nome | `nome` | não | sem nome, usa o código |
| fabricante | `fabricante` | não | plano B: coluna com "fabric" no nome; vazio vira "Sem fabricante" |
| estoque atual | `estoque_atual` | sim | |
| quantidade vendida | `quantidade_vendida` | sim | o período (`{ultimos_90_dias}`) precisa ser igual ao "Período das vendas" |

## Como calcula

1. Saída por dia = quantidade vendida ÷ período (dias). Cobertura = estoque ÷ saída por dia (zero ou negativo = 0; sem venda = sem giro).
2. Sugestão de compra = saída por dia × dias da projeção − estoque (negativo pode contar como zero), nunca negativa.
3. Curva ABC (Pareto pela quantidade vendida, % acumulado antes do item): A até o corte A, B até o corte B, o resto C.
4. Status e prioridade:

| Status | Regra |
|---|---|
| 🔴 Ruptura, comprar já | vende e está com estoque zero ou negativo |
| 🟠 Comprar urgente | cobertura até o limite crítico da curva |
| 🟡 Comprar | cobertura até o limite de atenção da curva |
| 🟢 Estoque saudável | entre atenção e excesso |
| 🔵 Excesso de estoque | cobertura a partir do limite de excesso da curva |
| ⚫ Estoque parado | tem estoque e não vendeu no período |
| ⚪ Zerado sem giro | sem estoque e sem venda |

Prioridade: tabela fixa por status e curva (mostrada em Configurações). Produtos com o nome em "Produtos ignorados" ficam fora.

## Banco

Ao instalar, o Waipe Páginas cria o schema `giro` com as tabelas padrão (cargas, histórico, configuração, integração) e a
tabela `giro.produtos`, uma linha por item (chave + empresa) e uma coluna por campo:

| Campo | Tipo |
|---|---|
| `codigo` | texto |
| `nome` | texto |
| `fabricante` | texto |
| `estoque_atual` | numero |
| `quantidade_vendida` | numero |
| `saida_por_dia` | numero |
| `cobertura_dias` | inteiro |
| `sugestao_compra` | inteiro |
| `curva_abc` | texto |
| `status` | texto |
| `prioridade` | texto |

Índices: (fabricante), (status). Migrações explícitas: nenhuma (coluna nova entra sozinha ao atualizar).

## Telas

- **Indicadores**: produtos ativos, ação imediata, itens a comprar, sugestão (un.), estoque parado (un.), cobertura
  mediana; saúde do estoque por status, matriz curva × status, curva ABC, evolução diária, comprar agora (top 12),
  faixas de cobertura e rankings de fabricantes (ação imediata e estoque parado). Imprimir e Excel.
- **Relatório de giro**: todos os produtos, filtros por fabricante, curva, status e prioridade; ordem por status.
- **Fabricantes**: ranking por ação imediata, com contagem por status.
- **Detalhe**: dados do produto e histórico de mudanças.

## Configurações

| Parâmetro | Padrão | O que muda |
|---|---|---|
| Período das vendas | 90 dias | divisor da saída por dia (trava: só muda depois de mudar o Data Lab) |
| Comprar para | 45 dias | sugestão de compra |
| Tratar estoque negativo como zero | não | sugestão de compra |
| Curva A até / Curva B até | 80% / 95% | cortes da curva ABC |
| Cobertura por curva | A 10/20/90, B 7/15/150, C 5/10/180 | limites de urgente, comprar e excesso |
| Texto para produto sem fabricante | Sem fabricante | agrupamento |
| Produtos ignorados | CONSUMIDOR FINAL | quem fica fora |

## Perguntas para personalizar

1. Qual o período de vendas do relatório (90 dias é o padrão) e para quantos dias comprar?
2. Os cortes da curva ABC e os dias de cobertura por curva fazem sentido para o ritmo de reposição do cliente?
3. O relatório traz o fabricante? Agrupar por fabricante ou por outra coluna (grupo, linha)?
4. Estoque negativo deve contar como zero na sugestão?

## Como instalar e testar

1. Waipe Páginas > Configurações gerais > Páginas > Instalar página (.json): `giro.json`.
2. Na página, Configurações > Integração: crie o relatório no Data Lab com o texto acima, cole o ID, baixe e importe
   os dois flows, ative e cole a URL do webhook.
3. Clique em Atualizar agora e confira um produto conhecido na tela de detalhe (saída por dia, cobertura e status).
4. `exemplo.json` traz linhas fictícias no formato do Data Lab.

## Histórico

### v2.1.0 (2026-11-19)
- Seções `integracao` (passos e horário 07:00 do flow agendado) e `exportar` (Excel, CSV e Imprimir) no plugin (Waipe Páginas 2.1.0).

### v2.0.0 (2026-11-19)
- Seção `banco`: a instalação cria a tabela da página com uma coluna por campo (Waipe Páginas 2.0.0).

### v1.0.0 (2026-11-19)
- Primeira versão como plugin (antes era código dentro do Waipe Páginas; regras iguais).
