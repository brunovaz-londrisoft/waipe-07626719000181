---
nome: Guardião da Amostra Padrão
slug: guardiao-da-amostra-padrao
versao: 1.2.0
modelo_base: nenhum
gatilho: agendado (dias 4 e 15 de cada mês, 07:00, America/Sao_Paulo)
icone: 🛡️
resumo: Ranking de clientes adormecidos (mais de 40 dias sem comprar) com a planilha de cada vendedor.
frequencia: Dias 4 e 15 de cada mês, 07:00
quem_recebe: Gestor comercial
nota: Este fluxo não envia mensagem aos vendedores: só o consolidado ao gestor.
atualizado: 2026-10-22
---

# Guardião da Amostra Padrão

## Quando usar

Cliente que quer **reativar clientes adormecidos**: os que compraram nos últimos 12 meses mas estão há mais de X dias
sem comprar (padrão: 40). O flow separa por vendedor (representante), cria uma planilha do Google Sheets para cada
um com a lista de clientes (nome, data da última compra, telefone e e-mail) e manda ao gestor um e-mail consolidado
com o ranking de vendedores e o botão de cada lista. Se não houver nenhum cliente adormecido, avisa por e-mail.

Modelos de comunicação (consolidado e planilha): `.claude/waipe/catalogo/guardiao-da-amostra-padrao/modelos/` (lista das peças em `modelos.json`).

Palavras-chave: clientes adormecidos, inativos, reativação, última compra, carteira, vendedor, planilha por vendedor.

## Perguntas para personalizar

Pergunte ao usuário (proponha o padrão entre parênteses):

1. **Nome da empresa** e **nome do gestor** que recebe o e-mail (vão no texto e no cabeçalho do e-mail).
2. **E-mail do gestor** (destino do consolidado).
3. **Quantos dias sem comprar** define "adormecido"? (padrão: 40).
4. **Quando rodar** (padrão: dias 4 e 15 de cada mês, 07:00). Dias, horário e fuso, ou só manual.
5. **Clientes a ignorar** além do "CONSUMIDOR FINAL" (padrão: só ele).
6. **Acesso às planilhas**: cada planilha de vendedor e a planilha-índice ficam visíveis para **qualquer pessoa com o
   link** (padrão do modelo) e contêm nome, telefone e e-mail de clientes. O cliente aceita? Se não, mude
   `sharing` para `private` nos nodes de criar planilha (o botão do e-mail só abrirá para quem tiver acesso à conta).
7. **Os vendedores aparecem no relatório de clientes?** O nome do vendedor precisa vir preenchido no Data Lab; sem ele,
   todos caem em "SEM VENDEDOR".

## Objetivo

Encontra os clientes que compraram nos últimos 12 meses mas **não compram há mais de 40 dias** (clientes
adormecidos), separa por vendedor (representante), cria uma planilha no Google Sheets para cada vendedor com a lista
de clientes e envia ao gestor um e-mail consolidado com o ranking e o botão de cada lista. Quando não há nenhum
cliente adormecido, envia um e-mail curto avisando que não houve nenhum.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Mensal, nos dias 4 e 15, às 07:00 (`America/Sao_Paulo`). |
| 2 | Clientes 12 Meses | waipe_data | Relatório do Data Lab com os clientes que compraram em 12 meses. |
| 3 | Processar Adormecidos | code | Ignora CONSUMIDOR FINAL e datas `1900-01-01`, fica com a compra mais recente de cada cliente, mantém quem comprou há mais de 40 dias (e até 365), agrupa por vendedor e ordena do maior para o menor. |
| 4 | Tem Adormecidos? | if | `true` segue para as planilhas; `false` vai para o aviso de "nenhum adormecido". |
| 5 | Criar Planilha Índice | google_sheets (create) | Cria uma planilha da execução, com leitura para qualquer pessoa com o link, para guardar o link de cada vendedor. |
| 6 | Cada Vendedor | loop | Percorre os vendedores um por vez; segue mesmo se um falhar. |
| 7 | Criar Planilha do Vendedor | google_sheets (create) | Cria "Clientes Adormecidos - <vendedor> - <dd-mm-aaaa>" com leitura para qualquer pessoa com o link. |
| 8 | Gravar Clientes na Planilha | google_sheets (append) | Grava as colunas Cliente, Última compra, Telefone e E-mail (do mais antigo para o mais recente). |
| 9 | Montar Linha do Índice | code | Monta a linha `Vendedor`, `Clientes`, `Link` (link da planilha recém-criada). |
| 10 | Registrar no Índice | google_sheets (append) | Grava essa linha na planilha-índice. |
| 11 | Ler Índice | google_sheets (read) | Depois do loop, lê o índice (a saída `done` do loop não devolve os links das planilhas criadas). |
| 12 | Montar E-mail Consolidado | code | Gera o HTML do e-mail: KPIs, ranking com barras e o botão → de cada vendedor apontando para a planilha dele. |
| 13 | Montar E-mail Sem Adormecidos | code | Gera o HTML curto de "nenhum cliente adormecido". |
| 14 | Enviar E-mail ao Gestor | gmail_send | Envia o HTML (os nodes 12 e 13 apontam para ele; só um dos dois executa). |

**Regra do corte:** adormecido é quem teve a última compra há **mais de 40 dias** (`diasSemComprar`) e há no máximo
365 dias (`janelaDiasCompra`). Cliente sem vendedor entra em "SEM VENDEDOR". Se o relatório vier com várias linhas do
mesmo cliente, vale a compra mais recente (clientes com o mesmo nome contam como um só).

**Links das planilhas:** a saída `done` do loop só devolve os vendedores originais, sem os links criados dentro dele.
Por isso o link de cada planilha é gravado numa planilha-índice dentro do loop e relido antes de montar o e-mail. Se um
vendedor falhar no loop, ele aparece no ranking com "-" no lugar do botão.

**Colunas do relatório:** o node Processar Adormecidos registra no log (console) os nomes de coluna recebidos e quais
foram usadas. Se o vendedor não for reconhecido, todos caem em "SEM VENDEDOR": confira o log e acrescente o nome da
coluna em `CONFIG.aliases.vendedor`. O node tem limite de 5 segundos: se o relatório for muito grande, filtre no próprio
Data Lab (só quem comprou nos últimos 12 meses, um registro por cliente).

**Textos de "semanal":** o HTML do e-mail diz "Relatório semanal" no cabeçalho e o aviso de silêncio diz "esta
semana", mas o agendamento do modelo é mensal (dias 4 e 15). Ajuste os textos nos nodes Montar E-mail Consolidado e
Montar E-mail Sem Adormecidos para combinar com a frequência escolhida.

## Como implantar em um cliente novo (passo a passo)

Pré-requisitos do cliente: ERP Gestor conectado ao Waipe (Data Lab), conta Google que vai rodar o flow (Sheets e Gmail)
e o e-mail do gestor.

1. **Criar o agente no repositório do cliente.** No Claude Code, peça "quero criar o agente Guardião da Amostra Padrão".
   A skill `waipe-criar-agente` copia este modelo e faz as perguntas acima. (Manual: `waipe.py novo-agente
   guardiao-da-amostra-padrao` e copie o `.json` e o `.md` para `agentes/guardiao-da-amostra-padrao/`.)
2. **Criar o relatório no Data Lab** com o texto da seção "Relatório do Data Lab" abaixo. Anote o ID.
3. **Importar o JSON** no Waipe Flow e preencher a configuração (seção "Configuração após importar").
4. **Ajustar o `CONFIG`** dos nodes de código com os dados do cliente (tabelas abaixo).
5. **Testar** (seção "Como testar"): rode pelo editor com o destino trocado por um e-mail de teste.
6. **Ativar** o flow (ele entra inativo) e acompanhar a primeira execução agendada.
7. **Fechar a release** do agente no cliente (`waipe-fechar-release`) e anotar no `CLAUDE.md` do cliente as
   particularidades (gestor, limite de dias, clientes ignorados).

## Configuração após importar

- **Credencial Google**: conectar a conta Google nos cinco nodes de Google Sheets (Criar Planilha Índice, Criar
  Planilha do Vendedor, Gravar Clientes na Planilha, Registrar no Índice, Ler Índice) e no Gmail.
- **Relatório do Data Lab** (node Clientes 12 Meses): trocar `SUBSTITUA_PELO_ID_DO_RELATORIO` pelo ID do relatório criado.
- **Destinatário** (node Enviar E-mail ao Gestor): trocar `gestor@exemplo.com` pelo e-mail do gestor.
- **Agendamento**: o flow entra inativo ao importar; ajuste dias e horário se preciso e ative.
- **Planilhas públicas**: cada planilha de vendedor **e a planilha-índice** (que reúne os links de todas) ficam
  visíveis para quem tiver o link, e as listas contêm nome, telefone e e-mail de clientes. Só compartilhe o e-mail
  com quem pode ver esses dados.

### Relatório do Data Lab (texto para criar)

Crie um relatório no Data Lab com este pedido em linguagem natural:

> Liste os clientes que compraram nos {ultimos_12_meses} meses. Colunas: código do cliente (codigo), nome do cliente
> (nome), data da última compra do cliente (dtultimacompra), telefone fixo do cliente (fone), celular do cliente
> (celular) e e-mail do cliente (email). código do vendedor/representante responsável pelo cliente
> (vendedor_codigo), nome do vendedor/representante (vendedor). A data da última compra deve ser a data da venda
> ou orçamento mais recente do cliente, sem considerar vendas canceladas.

Pontos de atenção: `{ultimos_12_meses}` é um parâmetro do Data Lab e precisa ter valor padrão. "Venda ou orçamento"
faz um cliente com orçamento recente parecer ativo, então ele não entra como adormecido: tire o "ou orçamento" se só
a compra deve contar. O nome do vendedor (`vendedor`) precisa vir preenchido. O flow usa as colunas `nome`,
`dtultimacompra`, `vendedor`, `fone`, `celular` e `email` (`fone` e `celular` são juntados na célula Telefone);
`codigo` e `vendedor_codigo` não são usados. Os nomes aceitos estão em `CONFIG.aliases` do node Processar Adormecidos.

### `CONFIG` de Processar Adormecidos

| Constante | Valor | Controla |
|---|---|---|
| `diasSemComprar` | `40` | Adormecido = última compra há mais de X dias. |
| `janelaDiasCompra` | `365` | Só considera quem comprou nesse período (12 meses). |
| `nomesIgnorados` | `["CONSUMIDOR FINAL"]` | Clientes descartados. |
| `nomeSemVendedor` | `SEM VENDEDOR` | Grupo para cliente sem vendedor. |
| `nomeAba` | `Página1` | Nome da primeira aba das planilhas novas (muda se a conta Google não estiver em português). |
| `aliases` | ver node | Nomes aceitos das colunas do relatório. |
| `trechos` | ver node | Plano B: trechos que o nome da coluna deve conter (ex.: `vend`) quando nenhum nome de `aliases` bate. |

### `CONFIG` de Montar E-mail Consolidado e Montar E-mail Sem Adormecidos

| Constante | Valor no modelo | Controla |
|---|---|---|
| `nomeEmpresa` | `NOME DA EMPRESA` | Nome da empresa no cabeçalho, no rodapé e no texto. |
| `nomeGestor` | `Nome do Gestor` | Nome na saudação do e-mail. |
| `titulo` | conforme o node | Título do e-mail. |
| `assunto` | conforme o node | Assunto do e-mail (contém o nome da empresa: troque). |

## Como testar

1. Importe `guardiao-da-amostra-padrao.json` no Waipe Flow (Dashboard → Importar JSON) e preencha a configuração.
2. Troque o `to` do Enviar E-mail ao Gestor por um e-mail de teste e rode pelo editor (não precisa esperar o dia 4 ou 15).
3. Esperado: uma planilha por vendedor no Drive, com a lista de clientes, uma planilha-índice com os links e um e-mail
   com KPIs, ranking e um botão → por vendedor abrindo a planilha. Confira os links, a aba das planilhas e se o
   CONSUMIDOR FINAL ficou de fora.
4. Para testar o aviso de silêncio, suba temporariamente `diasSemComprar` para um valor muito alto (ex.: 1000).
5. Volte o destino para o do gestor e **ative o flow**.

## Histórico

### v1.2.0 (2026-10-22)
- E-mails no novo padrão de e-mail Waipe (claro, com modo escuro automático, desenho do Guardião da Amostra Padrão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `modelos/`, dentro da pasta do modelo, só com as peças enviadas, gerados rodando os nodes com dados fictícios.

### v1.1.0 (2026-10-22)
- E-mails do consolidado e do aviso de "nenhum adormecido" no padrão de e-mail Waipe (tema escuro, destaque com o total, ranking com botão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `.claude/waipe/catalogo/guardiao-da-amostra-padrao/modelos/` (lista das peças em `modelos.json`).

### v1.0.0 (2026-10-16)
- Primeira versão do modelo no catálogo, anonimizada a partir do agente em produção em um cliente (Data Lab, e-mails,
  nomes e empresa trocados por placeholders; texto do relatório do Data Lab documentado).
