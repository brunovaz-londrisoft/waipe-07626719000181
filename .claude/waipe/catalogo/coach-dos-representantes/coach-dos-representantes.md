---
nome: Coach dos Representantes
slug: coach-dos-representantes
versao: 1.0.0
modelo_base: nenhum
gatilho: agendado (segunda e quinta-feira, 07:00, America/Sao_Paulo)
atualizado: 2026-10-16
---

# Coach dos Representantes

## Quando usar

Cliente com equipe de vendedores (representantes) no ERP Gestor que quer **acompanhamento periódico de performance**:
cada vendedor recebe o próprio resumo (vendas do mês contra a meta, carteira de clientes, pendências) e o gestor
recebe um consolidado de todos. Serve para qualquer cliente que tenha vendas, carteira de clientes e cadastro de
vendedores no Gestor (via Data Lab) e metas numa planilha do Google Sheets.

Palavras-chave: vendedores, representantes, metas, comissão, carteira de clientes, resumo semanal, WhatsApp, PDF.

## Perguntas para personalizar

Pergunte ao usuário, nesta ordem (proponha o padrão entre parênteses):

1. **Nome da empresa** e **nome do gestor** que recebe o consolidado (vão no texto das mensagens).
2. **E-mail do gestor** (destino do consolidado).
3. **Quando rodar** (padrão: segunda e quinta, 07:00). Dias, horário e fuso.
4. **Contato de dúvidas** que aparece no rodapé das mensagens aos vendedores: nome e WhatsApp.
5. **Existe um vendedor "genérico"** (ex.: Televendas, B2C) cujas vendas devem ser agrupadas à parte? Qual o código
   dele no ERP? (padrão: nenhum).
6. **Canal de envio aos vendedores**: WhatsApp pela Z-API oficial (padrão, com e-mail para quem não tem telefone).
   O cliente já tem a instância Z-API oficial? Se ainda não, use o modo de testes (ver "Configuração após importar").
7. **A planilha de metas já existe?** Se não, será criada com o flow auxiliar `adicionar-vendedores-em-metas`.

## Objetivo

Acompanhamento periódico de performance por vendedor. Cruza as vendas do mês, a carteira de clientes, o cadastro de
vendedores (Data Lab) e as metas (Google Sheets). Envia a cada vendedor um resumo individual com PDF por WhatsApp
(Z-API oficial), ou por e-mail quando ele não tem telefone, e manda ao gestor um relatório consolidado por e-mail.

**Flow auxiliar nesta pasta:** [`adicionar-vendedores-em-metas.json`](adicionar-vendedores-em-metas.md) acrescenta à
planilha de metas os vendedores do ERP que ainda não estão nela (pelo código), com meta `0`, sem alterar as linhas
existentes. Rode antes do Coach na primeira instalação e sempre que entrar vendedor novo. É um flow de manutenção:
**não fica ativo no cliente**.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Semanal, segunda e quinta-feira às 07:00 (`America/Sao_Paulo`, `weekdays: 1,4`). |
| 2 | Vendas do mes | waipe_data | Relatório do Data Lab com as vendas e orçamentos do mês. |
| 3 | Clientes | waipe_data | Relatório do Data Lab com a carteira de clientes. |
| 4 | Vendedores | waipe_data | Relatório do Data Lab com o cadastro de vendedores. |
| 5 | Metas por Vendedor | google_sheets | Lê a planilha de metas (aba `Página1`). |
| 6 | Processar Carteiras | code | Cruza vendas, clientes, vendedores e metas e agrupa por código de vendedor normalizado. Valida telefone e e-mail de cada vendedor. |
| 7 | Cada Vendedor | loop | Percorre os vendedores um por vez; segue mesmo se um falhar. |
| 8 | Montar Mensagens do Vendedor | code | Monta o texto do WhatsApp, o resumo por e-mail e o HTML do PDF do vendedor. |
| 9 | Criar Documento do Vendedor | google_docs | Cria o documento "Relatorio - <nome>" com o HTML do PDF. |
| 10 | Exportar PDF do Vendedor | google_drive | Exporta o documento como PDF (base64). |
| 11 | Rotear por Contato | switch | `com_telefone` vai para o WhatsApp; `com_email` vai para o e-mail (os dois, se tiver os dois); `sem_contato` (fallback) vai para o node 16. |
| 12 | Enviar WhatsApp com PDF | http_request | POST na Z-API oficial (`api.z-api.io`, `send-document/pdf`): PDF anexado com a mensagem como legenda. |
| 13 | Enviar E-mail ao Vendedor | gmail_send | Envia o resumo por e-mail. |
| 14 | Montar E-mail do Gestor | code | Ao fim do loop, monta o e-mail consolidado do gestor. |
| 15 | Enviar Relatório ao Gestor | gmail_send | Envia o consolidado ao gestor. |
| 16 | Vendedor sem Contato | edit_fields | Fim da linha para quem não tem telefone nem e-mail válidos: não envia nada, só marca `envio`. |

O WhatsApp sai pela Z-API oficial por `http_request`, **não** pelo node `zapi_send`: o PDF em Base64 passa de 256 KB
(teto de qualquer expressão do Waipe Flow; um PDF real deu 612 KB) e o `zapi_send` falha com
`ExpressionResultTooLarge`. Só os campos do corpo do `http_request` têm teto de 4 MiB.

**Validação de contato** (Processar Carteiras): telefone válido = `55` + DDD (dois dígitos de 1 a 9) + 8 dígitos
(fixo) ou 9 dígitos começando com 9 (celular), depois de tirar máscara e acrescentar o `55` quando faltar. E-mail
válido = texto com `@` e um domínio com ponto (ex.: `nome@exemplo.com`). Contato inválido fica vazio para o roteamento (não tenta enviar) e entra no e-mail do
gestor, em "Pendências de cadastro", com nome, código e motivo. O fallback `sem_contato` existe porque, sem ele, o
Waipe Flow manda o item que não casa com nenhuma regra para a primeira saída do switch.

**Grupo genérico (ex.: Televendas):** o código informado em `CONFIG.codigoTelevendas` é agrupado como `TELEVENDAS` só
para somar as vendas. O nome exibido vem sempre do cadastro real do vendedor no ERP.

**Destinos:**

| Node | Campo | Valor no modelo |
|---|---|---|
| Enviar WhatsApp com PDF | Corpo JSON, campo `phone` | `{{ $node["Montar Mensagens do Vendedor"].json.telefone }}` (telefone do cadastro do vendedor) |
| Enviar E-mail ao Vendedor | Para (`to`) | `{{ $node["Montar Mensagens do Vendedor"].json.email }}` (e-mail do vendedor) |
| Enviar Relatório ao Gestor | Para (`to`) | `gestor@exemplo.com` (trocar pelo e-mail do gestor) |

## Como implantar em um cliente novo (passo a passo)

Pré-requisitos do cliente: ERP Gestor conectado ao Waipe (Data Lab), conta Google que vai rodar os flows,
instância Z-API oficial (ID, token da instância e Client-Token) e a lista dos vendedores com telefone e/ou e-mail
cadastrados no ERP.

1. **Criar o agente no repositório do cliente.** No Claude Code, peça "quero criar o agente Coach dos Representantes".
   A skill `waipe-criar-agente` copia este modelo e faz as perguntas acima. (Manual: `waipe.py novo-agente
   coach-dos-representantes` e copie o `.json`, o `.md` e os arquivos do flow auxiliar para `agentes/coach-dos-representantes/`.)
2. **Criar os 3 relatórios no Data Lab** com os textos da seção "Relatórios do Data Lab" abaixo. Anote o ID de cada um.
3. **Criar a planilha de metas** no Google Drive da conta que vai rodar os flows: planilha em branco, primeira aba
   chamada `Página1`. Copie a URL.
4. **Importar o flow auxiliar** `adicionar-vendedores-em-metas.json` no Waipe Flow, preencher o ID do relatório de
   vendedores e a URL da planilha, conectar a conta Google e rodar uma vez. A planilha passa a ter `codigo`, `nome` e
   `meta` com todos os vendedores e meta `0`.
5. **Preencher as metas** na planilha: valor do mês **sem `R$`** (ex.: `150000` ou `150.000,00`), coluna sem formatação
   de moeda (`R$ 150.000,00` vira meta `0`). Centavos só com vírgula. **Apague a linha de quem não deve receber o
   resumo:** todo vendedor que está na planilha recebe, mesmo com meta `0`.
6. **Importar o `coach-dos-representantes.json`** e preencher o que o JSON não traz (seção "Configuração após importar").
7. **Ajustar o `CONFIG`** dos nodes de código com os dados do cliente (tabelas abaixo) e trocar o nome da empresa nos
   textos fixos (ver "Textos com o nome da empresa").
8. **Testar com contatos internos** (ver "Como testar"), conferir as mensagens e só então ativar o flow.
9. **Fechar a release** do agente no cliente (`waipe-fechar-release`) e anotar no `CLAUDE.md` do cliente as
   particularidades (gestor, contato de dúvidas, código do grupo genérico).

## Configuração após importar

O JSON **não tem credenciais** nem IDs do cliente: tudo abaixo precisa ser preenchido depois de importar.

- **Credenciais Google** (vêm vazias): conectar a conta Google em Metas por Vendedor, Criar Documento do Vendedor,
  Exportar PDF do Vendedor, Enviar E-mail ao Vendedor e Enviar Relatório ao Gestor.
- **Z-API oficial** (Enviar WhatsApp com PDF): na URL, trocar `SUBSTITUA_PELO_ID_DA_INSTANCIA` e
  `SUBSTITUA_PELO_TOKEN_DA_INSTANCIA` pelo ID e token da instância, e no header `Client-Token` trocar
  `SUBSTITUA_PELO_CLIENT_TOKEN` pelo Client-Token da conta. Esses valores **nunca** ficam no repositório. Enquanto o
  cliente não tem a instância oficial, os testes podem ir para a instância sandbox da Z-API
  (`https://frontzap.com.br/instances/<ID>/token/<TOKEN>/send-document/pdf`, mesmo corpo e header); ao virar produção,
  volte para `api.z-api.io`.
- **Relatórios do Data Lab**: trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDAS`, `..._DE_CLIENTES` e
  `..._DE_VENDEDORES` nos nodes Vendas do mes, Clientes e Vendedores.
- **Planilha de metas** (node Metas por Vendedor): trocar `SUBSTITUA_PELA_URL_DA_PLANILHA_DE_METAS` pela URL da
  planilha, aba `Página1`, cabeçalho na linha 1. Colunas lidas: `codigo` (ou `vendedor`), `meta`, e opcionais `email`
  (ou `e-mail`) e `comissao`.
- **Destinatário do gestor**: no node Enviar Relatório ao Gestor, trocar `gestor@exemplo.com`.
- **Agendamento**: o flow entra inativo ao importar; ajuste dias e horário se preciso e ative.

### Relatórios do Data Lab (textos para criar)

Crie três relatórios no Data Lab, com o sufixo do cliente no nome. O texto de cada um é o pedido em linguagem natural:

| Node | Nome sugerido | Texto do relatório |
|---|---|---|
| Vendedores | VENDEDORES (Coach dos Representantes) | `Gere uma lista completa com todos vendedores, incluindo todos os campos.` |
| Clientes | CLIENTES (Coach dos Representantes) | `Liste todos os clientes com todos os campos incluindo o campo vendedor` |
| Vendas do mes | VENDAS E ORÇAMENTOS DO MES (Coach dos Representantes) | `Gerar todas as vendas e orçamentos do {inicio_mes} até  {fim_mes} com todos campos disponíveis.` |

`{inicio_mes}` e `{fim_mes}` são parâmetros do Data Lab e precisam ter valor padrão (início e fim do mês corrente).

### `CONFIG` de Processar Carteiras

| Constante | Valor no modelo | Controla |
|---|---|---|
| `codigoTelevendas` | `""` (vazio) | Código de vendedor agrupado como `TELEVENDAS` nas vendas. Deixe vazio se o cliente não tem. |
| `emailGestor` | `gestor@exemplo.com` | E-mail do gestor no consolidado (o envio usa o `to` do node Gmail). |
| `nomeGestor` | `Nome do Gestor` | Nome do gestor no consolidado. |
| `assuntoEmailGestor` | `Relatório Consolidado Semanal - Coach de Vendas` | Assunto do e-mail do gestor. |
| `ocultarGruposSemAtividade` | `true` | Esconde grupos sem vendas nem carteira. |

### `CONFIG` de Montar Mensagens do Vendedor

| Constante | Valor no modelo | Controla |
|---|---|---|
| `limiteClientesResumo` | `10` | Quantos clientes aparecem no resumo do WhatsApp. |
| `nomeEmpresa` | `NOME DA EMPRESA` | Nome da empresa nos textos. |
| `contatoDuvidasNome` | `Nome do Responsável` | Quem atende dúvidas, no rodapé do WhatsApp e do e-mail. |
| `contatoDuvidasWhatsapp` | `(00) 00000-0000` | WhatsApp de dúvidas, no rodapé. |
| `orcamentoBytesTabela` | `180000` | Tamanho máximo das tabelas do e-mail e do PDF. O Waipe Flow derruba qualquer `{{ }}` acima de 262.144 bytes (`ExpressionResultTooLarge`); acima do orçamento a tabela é cortada e avisa quantos clientes ficaram de fora. |

### Textos com o nome da empresa

**Montar E-mail do Gestor** não tem bloco `CONFIG`: o nome da empresa está escrito direto no HTML (cabeçalho e
rodapé "Mensagem automática do sistema comercial NOME DA EMPRESA."). O assunto do node **Enviar E-mail ao Vendedor**
("Seu resumo semanal - Coach de Vendas NOME DA EMPRESA") também é fixo. Troque `NOME DA EMPRESA` nesses três pontos.

## Como testar

1. Importe `coach-dos-representantes.json` no Waipe Flow (Dashboard → Importar JSON) e preencha a configuração acima.
2. **Teste seguro:** antes de rodar, troque os destinos por contatos internos: no node Enviar WhatsApp com PDF, o
   campo `phone` por um número de teste; em Enviar E-mail ao Vendedor, o `to` por um e-mail de teste; em Enviar
   Relatório ao Gestor, o `to` por um e-mail de teste. Rode com poucos vendedores na planilha de metas.
3. Rode manualmente (o agendamento só vale com o flow ativo). Esperado: cada vendedor recebe o resumo com o PDF por
   WhatsApp (ou por e-mail, se não tiver telefone) e o gestor recebe o consolidado, com as pendências de cadastro.
4. Volte os destinos para os de produção, rode uma vez, confira e **ative o flow**.

Erros comuns: `ExpressionResultTooLarge` (PDF grande demais para `zapi_send`: use o `http_request` como está),
meta `0` para quem tem `R$` na célula (limpe a formatação), vendedor que não recebeu (confira se está na planilha e
se o telefone passa na validação).

## Histórico

### v1.0.0 (2026-10-16)
- Primeira versão do modelo no catálogo, anonimizada a partir do agente em produção em um cliente (Data Labs,
  planilha, destinatários, nomes e contatos trocados por placeholders; textos dos relatórios do Data Lab documentados).
