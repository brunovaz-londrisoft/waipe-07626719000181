---
nome: Guardião da Carteira - Monitoramento Comercial
slug: guardiao-da-carteira
versao: 1.0.0
modelo_base: nenhum
gatilho: agendado (toda sexta, 17:00, America/Sao_Paulo)
icone: 🧭
resumo: Cruza a última compra no Gestor com as interações do Ploomes e classifica cada cliente da carteira por cor, com planilha e e-mail ao gestor.
frequencia: Toda sexta, 17:00
quem_recebe: Gestor comercial
atualizado: 2026-10-23
---

# Guardião da Carteira - Monitoramento Comercial

## Quando usar

Cliente que usa o **Ploomes** (CRM) para registrar os contatos com clientes e quer ver a saúde da carteira toda semana:
o agente cruza a **data da última compra** de cada cliente no Gestor (Data Lab) com o **último contato** registrado no
Ploomes (18 meses), classifica cada cliente por cor (verde a vermelho) e entrega uma planilha nova e um e-mail ao gestor
com a distribuição por status.

Modelos de comunicação (e-mail ao gestor e planilha): `.claude/waipe/catalogo/guardiao-da-carteira/modelos/` (lista das peças em `modelos.json`). O e-mail segue o **padrão de e-mail Waipe**.

Palavras-chave: carteira de clientes, Ploomes, CRM, última compra, último contato, status, semáforo, planilha, gestor.

## Perguntas para personalizar

Pergunte ao usuário, nesta ordem (proponha o padrão entre parênteses):

1. **Nome da empresa** no e-mail (`CONFIG.nomeEmpresa` de "Montar E-mail do Relatório").
2. **E-mail do gestor** que recebe o relatório (campo `to` de "Enviar E-mail com o Relatório").
3. **Quando rodar** (toda sexta, 17:00).
4. **Faixas de status** em dias desde a última compra (verde até 15, azul até 30, amarelo até 60, laranja até 90,
   vermelho acima de 90 ou sem compra): ficam em `statusDe` de "Consolidar Clientes e Calcular Status".
5. **Vínculo com o Ploomes**: só por CPF/CNPJ (`SO_DOCUMENTO: true`, padrão) ou também por e-mail e telefone.
6. **Incluir contatos do Ploomes sem cadastro no Gestor** (`INCLUIR_SO_PLOOMES`, padrão não).

## Objetivo

Acompanhar a saúde da carteira: cruza a data da última venda de cada cliente (Gestor, via Data Lab) com a data do último
contato no Ploomes (interações dos últimos 18 meses), consolida uma linha por cliente, classifica o status por cor, grava
tudo numa planilha nova a cada execução e envia o resumo por e-mail.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Dispara toda sexta-feira, 17:00 (`America/Sao_Paulo`). |
| 2 | Entrada Datalab (Clientes e Vendas) | waipe_data | Relatório do Data Lab com os clientes e a data da última venda, por empresa do grupo. |
| 3 | Buscar Interações Ploomes (18 meses) | http_request | `GET /InteractionRecords` do Ploomes (`ContactId`, `Date`) dos últimos 18 meses, com paginação. |
| 4 | Extrair ContactIds Únicos | code | Deduplica os `ContactId` e monta lotes de 10 para consultar os contatos. |
| 5 | Buscar Dados dos Contatos Ploomes | http_request | `GET /Contacts` (com `Phones` e `Company`) para cada lote: documento, e-mail e telefone. |
| 6 | Consolidar Clientes e Calcular Status | code | Funde as vendas do Gestor em 1 linha por cliente, vincula ao Ploomes, calcula o status e a distribuição por faixa. |
| 7 | Criar Planilha do Resultado | google_sheets (create) | Cria "Monitoramento Comercial da Carteira - <data>". |
| 8 | Preparar Linhas da Planilha | code | Uma linha por cliente, com as datas em `AAAA-MM-DD`. |
| 9 | Preencher Planilha com Clientes | google_sheets (append) | Grava as linhas com `USER_ENTERED` (datas como data). |
| 10 | Consolidar Linhas Gravadas | merge_out | Junta as linhas gravadas antes do e-mail. |
| 11 | Montar E-mail do Relatório | code | E-mail no padrão Waipe: clientes que precisam de atenção, indicadores, distribuição por status e botão para a planilha. |
| 12 | Enviar E-mail com o Relatório | gmail_send | Envia o relatório ao gestor. |

O gatilho liga os nodes 2 e 3 em paralelo; o node 6 espera os dois ramos.

**Regra de status** (só a última compra no Gestor define a cor; o contato do Ploomes é informativo):

| Status | Última compra |
|---|---|
| 🟢 Verde | até 15 dias |
| 🔵 Azul | 16 a 30 dias |
| 🟡 Amarelo | 31 a 60 dias |
| 🟠 Laranja | 61 a 90 dias |
| 🔴 Vermelho | mais de 90 dias ou sem registro de compra |

**Vínculo Gestor x Ploomes:** pelo CPF/CNPJ primeiro. Documento compartilhado por mais de um cliente do Gestor só vincula
se houver também e-mail ou telefone em comum. Sem documento, vincula por e-mail ou telefone únicos (telefone = DDD + 8
últimos dígitos). E-mail ou telefone repetido em mais de 2 contatos é tratado como genérico e ignorado.

## Como implantar em um cliente novo

1. `waipe.py novo-agente <slug> --modelo guardiao-da-carteira` e responda às perguntas acima.
2. Crie o relatório do Data Lab com as colunas abaixo e cole o ID em "Entrada Datalab".
3. Ponha a chave de API do Ploomes do cliente nos dois nodes HTTP (cabeçalho `User-Key`), sem gravar no repositório.
4. Importe o JSON, conecte Google e Gmail e siga "Como testar".

## Configuração após importar

- **Credencial Google** (`credentialId` vazio): conectar nos dois nodes de Google Sheets e no Gmail.
- **Ploomes:** trocar `SUBSTITUA_PELA_CHAVE_DE_API_DO_PLOOMES` pela chave do cliente em "Buscar Interações Ploomes" e
  "Buscar Dados dos Contatos Ploomes". Não grave a chave real no repositório.
- **Relatório do Data Lab:** trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_CLIENTES_E_VENDAS` pelo ID do relatório.
- **Agendamento:** sexta, 17:00, `America/Sao_Paulo`. O flow entra inativo ao importar: ative depois do teste.

### Destinos

| Node | Campo | Teste | Produção |
|---|---|---|---|
| Enviar E-mail com o Relatório | `to` | e-mail interno de teste | e-mail do gestor (`gestor@exemplo.com` no modelo) |

### Relatórios do Data Lab (textos para criar)

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| Entrada Datalab (Clientes e Vendas) | Clientes com a última venda | Liste todos os clientes com código, nome/razão social, CPF/CNPJ, tipo de pessoa, e-mail, telefone, vendedor e a data da última venda (AAAA-MM-DD), uma linha por cliente e por empresa do grupo. |

Colunas esperadas (aliases aceitos no `CONFIG` de Consolidar): `codigo`, `nome_razao_social`, `cnpj_cpf`, e-mail,
telefone, `tipo_pessoa`, `vendedor`, `data_ultima_venda` e a empresa da venda (`_razaoOrigem`). O flow funde pelo código
do Gestor e fica com a venda mais recente.

### `CONFIG` de Consolidar Clientes e Calcular Status

| Constante | Valor | Controla |
|---|---|---|
| `FUSO_HORAS` | `-3` | Fuso usado para "hoje" e para as datas. |
| `INCLUIR_SO_PLOOMES` | `false` | `true` também lista contatos do Ploomes sem cadastro no Gestor. |
| `NODE_INTERACOES` | nome do node HTTP | Node de onde lê as interações. Se renomear o node, atualize aqui. |
| `SO_DOCUMENTO` | `true` | Cliente com CPF/CNPJ só vincula ao Ploomes por documento. |
| `MAX_POR_CHAVE` | `2` | E-mail/telefone compartilhado por mais que isso é genérico e não vincula. |
| `DL_*` / `PL_*` | listas de nomes | Nomes aceitos das colunas do Data Lab e dos campos do Ploomes. |
| `STATUS` | emojis e nomes | Rótulos de status gravados na planilha. |

### `CONFIG` de Montar E-mail do Relatório

| Constante | Valor | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Empresa no topo do e-mail. |
| `titulo` | `Monitoramento comercial da carteira` | Título do e-mail. |
| `assunto` | `Monitoramento comercial da carteira - {data}` | Assunto; `{data}` vira a data da execução. |
| `rodape` | mensagem automática | Primeira linha do rodapé. |

### `CONFIG` de Preparar Linhas e de Extrair ContactIds

- `CAMPOS_DATA` (`['uc', 'uv']`): colunas de data convertidas para `AAAA-MM-DD`.
- `TAMANHO_LOTE` (`10`) e `MAX_PAGINAS_HTTP` (`500`, igual ao `maxPages` do node de interações).

## Atenção

- A planilha está com `sharing: anyone_reader`: qualquer pessoa com o link lê nome, documento, e-mail e vendedor dos
  clientes. Avalie `private`.
- O node de código tem teto de cerca de 1 MiB de saída; o flow avisa no log quando a carteira se aproxima disso.
- Se o log mostrar "Nenhuma data de venda encontrada" ou "Nenhum CPF/CNPJ encontrado", confira as colunas do relatório e
  ajuste os `DL_*` do `CONFIG`.

## Como testar

1. Importe o JSON, conecte Google e Gmail, ponha a chave do Ploomes nos dois nodes HTTP e confira o relatório do Data Lab.
2. Ponha um e-mail interno de teste no node de Gmail e rode manualmente pelo editor.
3. Esperado: uma planilha nova com uma linha por cliente (Código do Gestor, Documento, Tipo, Nome/Razão Social, E-mail,
   último contato no Ploomes, última venda no Gestor, empresa da última venda, vendedor e status) e o e-mail com o total
   de clientes, vinculados ao Ploomes, sem contato em 18 meses e a distribuição por status.
4. Troque o destinatário para o do gestor e ative o flow.

## Histórico

### v1.0.0 (2026-10-23)
- Adotado como modelo do agente do cliente piloto (anônimo) `guardiao-da-carteira` v1.0.0, com os dados do cliente
  descaracterizados (destino, IDs, chave do Ploomes e exemplos).
- E-mail no padrão de e-mail Waipe, montado no node "Montar E-mail do Relatório"; o Consolidar passa a devolver a
  distribuição por status em dados (`faixas`). A planilha passa a `anyone_reader`.
