---
nome: Adicionar Vendedores em Metas - Coach dos Representantes
arquivo: adicionar-vendedores-em-metas.json
faz_parte_de: coach-dos-representantes
versao: 1.0.0
gatilho: manual
atualizado: 2026-10-16
---

# Adicionar Vendedores em Metas - Coach dos Representantes

Flow auxiliar do [Coach dos Representantes](coach-dos-representantes.md). Existe só para manter a planilha de metas
que o Coach lê. É um flow de **manutenção: não fica ativo no cliente**, só é importado e rodado quando preciso.

## Objetivo

Compara os vendedores cadastrados no ERP (Data Lab) com a planilha de metas **pelo código** e acrescenta no fim da
planilha só os que ainda não estão nela, com meta `0`. Linhas que já existem (código, nome e meta) nunca são
alteradas: o flow só lê a planilha e só escreve linhas novas.

Use na instalação (planilha em branco: ele cria o cabeçalho e traz todos os vendedores) e sempre que entrar
vendedor novo no ERP.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Manual | trigger_manual | Disparo manual. |
| 2 | Vendedores | waipe_data | Relatório do Data Lab com o cadastro de vendedores (o mesmo do Coach). |
| 3 | Planilha Atual | google_sheets (read) | Só **lê** `Página1!A1:Z`. |
| 4 | Montar Linhas Novas | code | Acha a coluna do código no cabeçalho (`codigo` ou `vendedor`), lista os códigos que já existem e separa os vendedores do ERP cujo código não está lá. Ignora vendedor sem código e código repetido. Decodifica entidades HTML nos nomes. |
| 5 | Tem Vendedor Novo? | if | `true` segue para gravar; `false` pula direto para a resposta (nada é escrito). |
| 6 | Adicionar Vendedores Novos | google_sheets (append) | Acrescenta as linhas novas ao fim, pelas colunas `codigo`, `nome` e `meta` do cabeçalho. |
| 7 | Responder Webhook | webhook_respond | Devolve `{ sucesso, vendedores_adicionados, ja_estavam_na_planilha }`. Com gatilho manual a resposta não vai a lugar nenhum, mas os números aparecem no resultado da execução. |

**Regras de segurança**
- A comparação é só pelo **código** (`12`, ` 12 ` e `12.0` valem o mesmo). Nome diferente entre ERP e planilha não
  gera linha nova nem altera nada.
- Se a linha 1 da planilha não tiver a coluna `codigo` (ou `vendedor`), o flow **falha sem escrever**, para não
  duplicar vendedores.
- Vendedor que saiu do ERP **não é removido** da planilha: apague a linha à mão.
- A gravação usa `extraDataHandling: error`: se faltar a coluna `codigo`, `nome` ou `meta` no cabeçalho, falha em vez de
  criar coluna nova. Colunas extras (`email`, `comissao`) ficam em branco nas linhas novas.

## Configuração após importar

- **Credencial Google** (o JSON vem sem credencial): conectar em Planilha Atual e Adicionar Vendedores Novos.
- **Relatório do Data Lab** (node Vendedores): trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDEDORES` pelo ID do relatório
  de vendedores do Coach (texto para criá-lo em [`coach-dos-representantes.md`](coach-dos-representantes.md)).
- **Planilha**: trocar `SUBSTITUA_PELA_URL_DA_PLANILHA_DE_METAS` pela URL da planilha de metas nos dois nodes de Google
  Sheets (a mesma do node Metas por Vendedor do Coach). A aba `Página1` aparece em dois lugares: o `sheetName` do
  append e o intervalo `Página1!A1:Z` do node Planilha Atual; se a aba tiver outro nome, troque nos dois.

Bloco `CONFIG` de **Montar Linhas Novas**:

| Constante | Valor | Controla |
|---|---|---|
| `COLUNAS_CODIGO` | `["codigo", "vendedor"]` | Cabeçalhos aceitos para a coluna do código (os mesmos que o Coach aceita). |
| `META_INICIAL` | `0` | Meta gravada nas linhas novas. |

## Como testar

1. Importe `adicionar-vendedores-em-metas.json` no Waipe Flow (Dashboard → Importar JSON) e conecte a credencial Google.
2. Faça antes uma cópia da planilha e aponte os dois nodes de Google Sheets para ela.
3. Apague uma linha de vendedor da cópia e rode manualmente.
4. Esperado: só esse vendedor volta, no fim da planilha, com meta `0`; nenhuma outra linha muda. Rodando de novo,
   `vendedores_adicionados` deve ser `0` e nada é escrito.
5. Confirme que a linha nova mantém o formato esperado (código como número ou texto, meta `0`).

## Histórico

### v1.0.0 (2026-10-16)
- Primeira versão no catálogo, anonimizada: só acrescenta ao fim da planilha os vendedores do ERP cujo código ainda
  não está nela, sem tocar nas linhas existentes.
