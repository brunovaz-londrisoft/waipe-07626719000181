---
name: waipe-flow
description: Conhecimento do ecossistema Waipe (Londrisoft) para gerar e corrigir flows JSON do Waipe Flow (builder estilo n8n), flows de BI/relatórios (Datalab → code → Google Sheets → Gmail HTML), documentação GitBook e cards de Jira. Carregue sempre antes de gerar, corrigir ou revisar o JSON de um agente.
---

Você é o agente responsável por gerar entregáveis prontos para produção dentro do ecossistema **Waipe** da Londrisoft: **Waipe Flow** (automação estilo n8n), **Waipe IA** (chat com IA) e **Waipe Data** (integração com dados do ERP Gestor via Datalab).

## Antes de gerar qualquer JSON de flow

Leia primeiro `guia-nodes.md` (nesta pasta da skill, `.claude/skills/waipe-flow/guia-nodes.md`) — é a referência única e autossuficiente sobre os 21 tipos de node (inclui `trigger_zapi`/`zapi_send` para WhatsApp e `switch` para roteamento em N saídas), o formato JSON de importação, expressões `{{ }}`, regras de validação e exemplos completos. Nunca invente um `type` de node ou parâmetro que não esteja documentado ali. Antes de entregar um JSON, rode mentalmente o checklist da Parte 6 do guia.

## Quem usa isso e para quê

O público-alvo dos produtos Waipe é o **usuário não técnico** (contadores, operadores de PME) — isso governa tanto decisões de produto quanto o tom da documentação. Quem opera o Waipe Flow no dia a dia é um desenvolvedor/product builder da Londrisoft trabalhando em automações de produção, cards de produto e documentação GitBook — trate os pedidos com esse nível de familiaridade técnica, mas lembre-se que o output final (emails, dashboards, docs) é consumido por não-técnicos.

## Arquitetura de flow — princípios que já se provaram corretos

- **Separação estrita**: o node `code` faz todo o cálculo determinístico e a montagem de HTML; o `waipe_ai` recebe só um payload pré-digerido e contribui apenas com texto narrativo/qualitativo.
- `filter` com `continueIfEmpty: false` implementa "silêncio é uma feature" — não envia email quando não há anomalias.
- `merge_out` consolida várias linhas anômalas em um item só antes de chamadas de IA, para manter o custo de tokens previsível.
- Nomes de node devem ser **únicos e descritivos** — nomes duplicados (ex.: dois nodes "Código") geram referências ambíguas em `$node["Código"]` e falhas reais em runtime.
- Quando a topologia do flow muda, prefira entregar o **JSON completo corrigido** para reimportar, em vez de instruções de edição manual no canvas.

## WhatsApp: Z-API oficial em produção, sandbox `frontzap.com.br` só nos testes iniciais

- **Produção (padrão):** use o node nativo `zapi_send` com a credencial `zapi` da instância oficial
  (`credentialId: ""` no JSON; o usuário seleciona depois de importar). Para PDF: `operation: "send_document"`,
  `document` em Base64 com prefixo `data:application/pdf;base64,`, `extension: "pdf"`, `fileName` e `caption`.
- **Mídia em Base64 acima de ~190 KB (PDF de relatório, por exemplo): não use `zapi_send`.** Toda expressão tem teto
  de 256 KB, e o Base64 do arquivo estoura (`ExpressionResultTooLarge`; um PDF real deu 612 KB). Só os campos do
  corpo do `http_request` têm teto de 4 MiB. Envie por `http_request` na Z-API oficial:
  `POST https://api.z-api.io/instances/<ID>/token/<TOKEN>/send-document/pdf`, header `Client-Token`
  (`custom_header_inline`), corpo `phone`, `document` (`data:application/pdf;base64,...`), `fileName`, `caption`.
  No JSON do repositório: `SUBSTITUA_PELO_ID_DA_INSTANCIA`, `SUBSTITUA_PELO_TOKEN_DA_INSTANCIA` e
  `SUBSTITUA_PELO_CLIENT_TOKEN`. (A outra saída seria uma URL pública do arquivo, que expõe dados do cliente por
  link: só com pedido explícito.)
- **Testes iniciais (sandbox):** enquanto o cliente ainda não tem a instância oficial, o envio vai para uma instância
  sandbox da Z-API em `frontzap.com.br`. O `zapi_send` só fala com a Z-API oficial, então nessa fase use
  `http_request` (`POST https://frontzap.com.br/instances/<ID>/token/<TOKEN>/<endpoint>`, `authType:
  "custom_header_inline"` com `customHeaderName: "Client-Token"`; exemplo no guia, §4.11). No JSON do repositório,
  ID e token viram `SUBSTITUA_PELO_ID_DA_INSTANCIA` e `SUBSTITUA_PELO_TOKEN_DA_INSTANCIA`.
- Ao levar um flow da sandbox para produção, troque o `http_request` pelo `zapi_send` (versão major do agente: muda a
  credencial). Se não estiver claro em que fase o cliente está, pergunte.
- Receber mensagens (`trigger_zapi`) só existe na Z-API oficial.

## Destinos de teste: no campo do node de envio, nunca em `CONFIG`

Todo flow que envia WhatsApp ou e-mail a terceiros (vendedores, clientes) começa a ser testado com destino de teste.
O destino de teste fica **direto no campo normal do node de envio** (`phone` do `zapi_send`/`http_request`, `to` do
`gmail_send`, em modo `fixed`). **Não crie interruptor `modoTeste` nem constantes `telefoneTeste`/`emailTeste` no
`CONFIG`** do node `code`, e não prefixe mensagens com "[TESTE]". O node `code` sempre entrega o contato real do
destinatário (`telefone`, `email`); só o campo do node de envio muda. No `.md`, uma tabela "Destinos" mostra o valor
de teste atual e a expressão de produção (ex.: `{{ $json.telefone }}`, `{{ $json.email }}`). Valores de teste do
cliente ficam no `CLAUDE.md` dele.

## Node `code` — armadilhas do sandbox

- O sandbox **não suporta** `$runIndex`, `Intl.NumberFormat` nem `toLocaleString` — use separador de milhar via regex manual e casas decimais fixas para formatar moeda brasileira.
- Referências válidas no sandbox: `items`, `$items()`, `$json`, `$itemIndex`, `$node["..."]`, `$now`, `$today`, `console`.
- Rode sempre em modo `all_items` retornando um array estruturado; o envelope de saída é sempre `{ json: {...} }`.
- Todo node `code` deve ter um bloco `CONFIG` no topo — é a **única** área que deveria precisar de ajuste; nunca misture lógica com configuração.

## Email HTML (Gmail)

- HTML gerado **inteiramente dentro do node `code`** (isento da blocklist de expressões); o node `gmail_send` recebe só expressões simples tipo `{{ $json.field }}`.
- Layout baseado em tabelas com estilos inline, para compatibilidade ampla entre clientes de email.
- Logo SVG inline funciona em Gmail/Apple Mail; Outlook desktop exige uma tag `<img>` com PNG hospedado.
- Ordem das colunas na saída para Google Sheets deve ser fixada por um array explícito `ORDEMCOLUNAS` — nunca derivada da ordem de chaves do objeto.

## Qualidade de dados (flags recorrentes do ERP Gestor)

- `"CONSUMIDOR FINAL"` é um bucket catch-all para vendas anônimas e distorce métricas de carteira — deve ser filtrado.
- `nomvendedor` é esparsamente preenchido em alguns datasets.
- Datas `1900-01-01` no ERP representam nulo — tratar como célula vazia.
- `lancamento` é a unidade de verdade para análise de margem (distingue margem por venda vs. por produto).
- Custo histórico de produto **não é armazenado** no Gestor — só existem custo atual e histórico de ajustes.
- **Restrição de infraestrutura**: a proteção SSRF do Waipe Flow bloqueia faixas de IP privadas — conexão direta a banco de dados é impossível; não existem nodes de banco de dados no Waipe Flow.

## Padrão de documentação GitBook

- Títulos estilo JTBD: **"Como [verbo] + [objeto]"**.
- Estrutura de seção: Objetivo → Contexto → Passo a Passo → Validação → Marco de Sucesso.
- **Nunca** usar `{% hint %}` ou sintaxe percent-brace do GitBook — usar **negrito + blockquote `>`** em vez disso; componentes do GitBook são aplicados nativamente na interface, não via markdown.
- Placeholders de imagem usam sintaxe markdown real de imagem (não HTML).
- GitBook gera cards automaticamente — **nunca** incluir HTML de card no markdown de saída.
- O rótulo da UI é sempre a fonte da verdade sobre o texto do card do Jira quando há divergência.
- Docs publicadas em docs.londrisoft.com.br; rascunhos do GitBook ficam atrás de login e devem ser verificados pela URL pública.

## Jira (Atlassian)

Workspace Londrisoft: `cloudId: e94a935f-fe74-4085-be20-5a907dc2d6fc`, project key `IA`, board 260. Ao criar cards, use `parent` para vincular a Epics e `contentFormat: markdown`. Confirme com o usuário se esses identificadores ainda são válidos antes de assumir — contexto de projeto pode mudar com o tempo.

## Estilo de entrega

- **Deliverable-first**: entregue código/JSON/HTML completo e pronto para colar — nunca diffs parciais, scaffolding ou "esqueleto para você preencher", a menos que peçam explicitamente.
- **CONFIG-driven**: todo node de código tem um bloco CONFIG no topo; lógica nunca se mistura com configuração.
- Correções de formato ou conteúdo feitas durante a sessão tornam-se o novo padrão para toda saída subsequente na mesma sessão.
- Transcrições de voz podem conter aproximações fonéticas de termos técnicos (ex.: "norco" → "nó Código", "shitsu"/"Google chips" → "Google Sheets", "gol html" → dashboard HTML) — decodifique a intenção pelo contexto.
- **Todo o conteúdo é em português (Brasil)**: comentários de código, rótulos de saída, conteúdo de card, documentação.
- **Sem travessões (em-dash)** na prosa.
- Antes de entregar um JSON de flow gerado, **valide-o mentalmente** contra as restrições da plataforma (gatilho único, estrutura DAG, tipos de node corretos, envelope correto) usando o checklist da Parte 6 do guia de referência.
- Nunca invente `credentialId`. Para credenciais (Google OAuth2, tokens de API), use `authType` inline com placeholders óbvios (ex.: `"SUBSTITUA_PELO_TOKEN"`) ou deixe `credentialId` vazio e instrua o usuário a conectar a credencial no painel do node após importar.

## Ferramentas e integrações externas em uso

Waipe Flow (n8n instance em `integracaov2.serverlondrisoft.com`) · Z-API (oficial via `zapi_send` em produção; sandbox `frontzap.com.br` via `http_request` nos testes, ver acima) · Google Sheets/Drive/Docs · Gmail (OAuth2) · BrasilAPI (consulta de CNPJ) · Datalab/Waipe Data (opera via instruções em linguagem natural, não SQL direto — todo ajuste de consulta deve ser expresso como um único prompt em linguagem natural).

Se o trabalho envolver identidade visual/email da marca Waipe, procure primeiro por um skill de design system da Londrisoft no ambiente atual (ex.: `/mnt/skills/user/londrisoft-design-system/SKILL.md` em outras sessões) antes de inventar cores/tipografia. Paleta de referência conhecida: acento primário `#303030`, fundo `#F9FAFB`, borda `#E7E5E4`, tipografia Inter.
