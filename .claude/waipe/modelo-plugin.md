---
nome: Nome legível da página
slug: {{slug}}
versao: 0.0.0
plataforma: 2.1.0
categoria: Produtos
modelo_base: nenhum
atualizado: {{data}}
---

# Nome legível da página

## Quando usar

Uma ou duas frases: para quem é e que pergunta a página responde todo dia. Palavras-chave para o catálogo.

## Objetivo

O que a pessoa vê e decide com esta página (e o que a página não faz).

## Relatório do Data Lab

Nome sugerido: **Nome do relatório**. Texto para criar (o mesmo de `dataLab.texto` no .json):

```
liste ...
```

| Coluna do relatório | Campo no plugin | Obrigatória | Observação |
|---|---|---|---|
| `nome_da_coluna` | `campo` | sim | nomes aceitos ficam em Configurações |

## Como calcula

Passo a passo do `calculo` do .json, em português: campos calculados, situações (com ícone e regra) e o que é
descartado. Cite os parâmetros pelo nome que aparece em Configurações.

| Situação | Regra |
|---|---|
| 🔴 Exemplo | condição |

## Banco

Ao instalar, o Waipe Páginas cria o schema `{{slug}}` com as tabelas padrão e a tabela de itens (seção `banco` do
.json): uma coluna por campo guardado.

| Campo | Tipo |
|---|---|
| `campo` | texto, numero, inteiro, data ou booleano |

Índices e migrações explícitas (renomear, remover, mudar tipo) por versão, se houver.

## Telas

- **Indicadores**: KPIs e blocos (o que cada um mostra e para onde o clique leva).
- **Relatório**: colunas, filtros em destaque, ordem padrão, filtro de período.
- **Consolidado** (se houver): por que agrupa e a ordem.
- **Detalhe** (se houver): o que mostra.

## Configurações

| Parâmetro | Padrão | O que muda |
|---|---|---|
| Nome em Configurações | valor | efeito |

## Perguntas para personalizar

1. Perguntas a fazer ao usar este plugin como base para outro cliente ou outra necessidade.

## Como instalar e testar

1. Waipe Páginas > Configurações gerais > Páginas > Instalar página (.json): `{{slug}}.json`.
2. Na página, Configurações > Integração: crie o relatório no Data Lab com o texto acima, cole o ID, baixe e importe
   os dois flows, ative e cole a URL do webhook.
3. Clique em Atualizar agora e confira: ...
4. `exemplo.json` traz linhas fictícias no formato do Data Lab (a validação roda o plugin com elas).

## Histórico

### Não publicado
- Primeira versão.
