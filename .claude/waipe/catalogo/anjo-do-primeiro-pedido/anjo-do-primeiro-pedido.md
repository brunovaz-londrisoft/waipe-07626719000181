---
nome: Anjo do Primeiro Pedido
slug: anjo-do-primeiro-pedido
versao: 1.1.0
modelo_base: nenhum
gatilho: agendado (toda terça-feira, 07:00, America/Sao_Paulo)
icone: 🪽
resumo: Radar dos clientes novos (uma compra só) de 20 a 40 dias sem recomprar, por WhatsApp e e-mail, e consolidado ao gestor.
frequencia: Toda terça-feira, 07:00
quem_recebe: Cada vendedor e o gestor comercial
atualizado: 2026-10-22
---

# Anjo do Primeiro Pedido

## Quando usar

Cliente que quer **fazer o cliente novo comprar de novo**: quem fez só 1 compra e já está há alguns dias sem recomprar
entra no "radar" do vendedor responsável. Cada vendedor recebe a lista dos seus clientes por WhatsApp e por e-mail, e o
gestor recebe um consolidado com a quantidade de cada vendedor. Serve para qualquer cliente com vendas e vendedores no
ERP Gestor (via Data Lab).

Palavras-chave: cliente novo, primeira compra, segunda compra, recompra, vendedor, radar, pós-venda, WhatsApp.

Modelos de comunicação (WhatsApp, e-mail, consolidado e planilha): `.claude/waipe/catalogo/anjo-do-primeiro-pedido/modelos/` (lista das peças em `modelos.json`).

## Perguntas para personalizar

1. **Nome da empresa**, **nome do gestor** e **contato de dúvidas** (nome e WhatsApp) que aparecem nas mensagens.
2. **E-mail do gestor** (destino do consolidado).
3. **Quando rodar** (padrão: toda terça, 07:00).
4. **Quantos dias sem comprar** colocam o cliente no radar (padrão: 20) e **até quantos dias** ele fica (padrão: 40; `0` = sem limite).
5. **Quantas compras definem "cliente novo"** (padrão: exatamente 1).
6. **Clientes a ignorar** além do CONSUMIDOR FINAL.
7. **Canal**: WhatsApp pela Z-API oficial (credencial `zapi`) e e-mail. O cliente já tem a instância oficial?
8. **Acesso às planilhas**: ficam visíveis para quem tiver o link e têm nome, telefone e e-mail de clientes. O cliente aceita?
9. O relatório de clientes traz **vendedor (código e nome)** e **quantidade de vendas** por cliente?

## Objetivo

Acompanha os **clientes novos**: quem fez **apenas 1 compra** em todo o histórico. Quando o cliente completa **20 dias sem
comprar de novo**, ele entra no **radar do vendedor** responsável e continua nele até comprar outra vez ou chegar a
**40 dias**. Cada vendedor recebe, por **WhatsApp**, os **10 clientes mais recentes no radar** (os de 20 dias primeiro) e o
**link da planilha completa**; quem tem e-mail recebe também a lista completa. Ao final, o **gestor** recebe um e-mail com
todos os vendedores, quanto cada um tem no radar, um botão para a planilha de cada um e a lista de quem não recebeu.

Se nenhum vendedor tem cliente no radar, o flow termina sem enviar nada.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Toda terça, 07:00 (`America/Sao_Paulo`). |
| 2 | Clientes | waipe_data | Relatório do Data Lab com todos os clientes, quantidade de vendas, última venda, contatos e vendedor. |
| 3 | Vendedores | waipe_data | Relatório do Data Lab com o cadastro de vendedores (telefone e e-mail). |
| 4 | Processar Radar | code | Junta as linhas do mesmo cliente, mantém quem tem 1 compra e de 20 a 40 dias sem comprar, ignora CONSUMIDOR FINAL, agrupa por vendedor (código, ou nome se faltar o código), valida o contato do vendedor e ordena do mais recente no radar para o mais antigo. |
| 5 | Tem Vendedor no Radar? | if | `true` segue; `false` encerra em silêncio. |
| 6 | Criar Planilha Índice | google_sheets (create) | Planilha privada da execução, para guardar o link da planilha de cada vendedor. |
| 7 | Cada Vendedor | loop | Um vendedor por vez; segue mesmo se um falhar. |
| 8 | Criar Planilha do Vendedor | google_sheets (create) | "Radar do Primeiro Pedido - <vendedor> - <data>", com leitura para qualquer pessoa com o link. |
| 9 | Gravar Clientes na Planilha | google_sheets (append) | Todos os clientes do vendedor, na mesma ordem. |
| 10 | Montar Linha do Índice | code | Linha `Vendedor`, `Clientes`, `Link`. |
| 11 | Registrar no Índice | google_sheets (append) | Grava a linha no índice. |
| 12 | Montar Mensagens do Vendedor | code | WhatsApp (10 primeiros e o link) e e-mail (lista completa e botão), este no padrão de e-mail Waipe. |
| 13 | Rotear por Contato | switch | `com_telefone` vai ao WhatsApp; `com_email` ao e-mail (os dois, se tiver); `sem_contato` ao node 16. |
| 14 | Enviar WhatsApp | zapi_send | Texto com o radar e o link da planilha (credencial `zapi`). |
| 15 | Enviar E-mail ao Vendedor | gmail_send | Lista completa em HTML. |
| 16 | Vendedor sem Contato | edit_fields | Fim da linha de quem não tem telefone nem e-mail válidos. |
| 17 | Ler Índice | google_sheets (read) | Depois do loop, lê o índice (a saída `done` não devolve os links criados no loop). |
| 18 | Montar E-mail do Gestor | code | Consolidado: destaque, ranking com botão e a seção "Vendedores que não receberam o radar" com os clientes de cada um. |
| 19 | Enviar E-mail ao Gestor | gmail_send | Envia o consolidado. |

**Regra do radar:** cliente novo = exatamente `qtdComprasNovo` compra(s) em todo o histórico; entra com `diasRadar` dias ou
mais sem comprar e sai ao comprar de novo ou ao passar de `diasMaximoRadar` dias.

**Links das planilhas:** a saída `done` do loop só devolve os vendedores originais, sem o que foi criado dentro dele. Por
isso cada link é gravado na planilha-índice dentro do loop e relido antes do e-mail do gestor.

**Contato do vendedor:** telefone válido = `55` + DDD + 8 dígitos (fixo) ou 9 dígitos começando com 9 (celular), tentando
`celular`, `telefone`, `fone`, `whatsapp` e `phone`; e-mail = texto com `@` e um domínio com ponto. Quem não tem nenhum dos dois não recebe e
aparece no e-mail do gestor, com o motivo.

**Destinos (produção):**

| Node | Campo | Valor |
|---|---|---|
| Enviar WhatsApp | `phone` | `{{ $node["Montar Mensagens do Vendedor"].json.telefone }}` |
| Enviar E-mail ao Vendedor | `to` | `{{ $node["Montar Mensagens do Vendedor"].json.email }}` |
| Enviar E-mail ao Gestor | `to` | `gestor@exemplo.com` (trocar) |

Para testar sem incomodar ninguém, troque os três campos por destinos fixos de teste e volte depois.

## Como implantar em um cliente novo

1. Peça "quero criar o agente Anjo do Primeiro Pedido": a skill `waipe-criar-agente` copia este modelo e faz as perguntas acima.
2. Crie os dois relatórios do Data Lab com os textos abaixo e cole os IDs nos nodes Clientes e Vendedores.
3. Importe o JSON, conecte a conta Google (Sheets e Gmail) e a credencial `zapi`.
4. Ajuste o `CONFIG` dos nodes de código, teste com destinos internos, volte os destinos e ative.

## Configuração após importar

O JSON **não tem credenciais** nem IDs do cliente.

- **Credenciais Google**: nos nodes de Google Sheets (Criar Planilha Índice, Criar Planilha do Vendedor, Gravar Clientes na Planilha, Registrar no Índice, Ler Índice) e no Gmail (e-mail ao vendedor e ao gestor).
- **Credencial Z-API** (tipo `zapi`): no node Enviar WhatsApp.
- **Relatórios do Data Lab**: trocar `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_CLIENTES` e `SUBSTITUA_PELO_ID_DO_RELATORIO_DE_VENDEDORES`.
- **Destinatário do gestor**: `gestor@exemplo.com` no node Enviar E-mail ao Gestor.
- **Agendamento**: o flow entra inativo; ative depois do teste.

### Relatórios do Data Lab (textos para criar)

| Node | Texto do relatório |
|---|---|
| Clientes | `Liste todos os clientes. Colunas: código do cliente (codigo), nome do cliente (nome), quantidade de vendas efetivadas do cliente (qtd_compras), data da última venda (dtultimacompra), telefone fixo (fone), celular (celular), e-mail (email), código do vendedor responsável (vendedor_codigo) e nome do vendedor (vendedor). Considere só vendas, sem orçamentos e sem vendas canceladas.` |
| Vendedores | `Gere uma lista completa com todos vendedores, incluindo todos os campos.` |

`qtd_compras` deve contar **vendas** (uma por pedido), não itens de produto, e sem contar orçamentos. O nome do vendedor e
o telefone e e-mail do cliente precisam vir preenchidos. Os nomes aceitos de cada coluna estão em `CONFIG.aliases`.

`CONFIG` de **Processar Radar**:

| Constante | Valor | Controla |
|---|---|---|
| `diasRadar` | `20` | Entra no radar com X dias ou mais sem comprar. |
| `diasMaximoRadar` | `40` | Sai do radar com mais de X dias (`0` = sem limite). |
| `qtdComprasNovo` | `1` | Cliente novo = exatamente X compras no histórico. |
| `nomesIgnorados` | `["CONSUMIDOR FINAL"]` | Clientes descartados. |
| `nomeSemVendedor` | `SEM VENDEDOR` | Nome do grupo de clientes sem vendedor. |
| `nomeAba` | `Página1` | Nome da primeira aba das planilhas novas (muda se a conta Google não estiver em português). |
| `aliases` | ver node | Nomes aceitos das colunas do relatório. |

`CONFIG` de **Montar Mensagens do Vendedor**: `limiteClientesWhatsapp` (10), `limiteClientesEmail` (500), `tamanhoMaximoNome` (32),
`nomeEmpresa`, `contatoDuvidasNome` e `contatoDuvidasWhatsapp` (rodapé). `CONFIG` de **Montar E-mail do Gestor**:
`nomeEmpresa`, `nomeGestor`, `titulo`, `assunto`, `rodape`, `maxClientesPorPendencia`.

## Como testar

1. Importe `anjo-do-primeiro-pedido.json` no Waipe Flow e preencha a configuração.
2. Troque os três destinos por destinos de teste e rode pelo editor.
3. Confira: só clientes com 1 compra e 20 a 40 dias, do mais recente no radar para o mais antigo; CONSUMIDOR FINAL fora; o link da planilha no WhatsApp; o botão de cada vendedor no e-mail do gestor; a seção de quem não recebeu. O log do node Processar Radar mostra as colunas lidas e os grupos.
4. Volte os destinos para os de produção e ative.

## Histórico

### v1.1.0 (2026-10-22)
- E-mails no novo padrão de e-mail Waipe (claro, com modo escuro automático, desenho do Guardião da Amostra Padrão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `modelos/`, dentro da pasta do modelo, só com as peças enviadas, gerados rodando os nodes com dados fictícios.

### v1.0.0 (2026-10-22)
- Primeira versão do modelo no catálogo, anonimizada a partir de um agente em produção em um cliente, com os e-mails no padrão Waipe.
