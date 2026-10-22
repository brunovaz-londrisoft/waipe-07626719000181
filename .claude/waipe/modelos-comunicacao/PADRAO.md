# Modelos de comunicação dos agentes (padrão v3)

Os **modelos de comunicação** mostram, com dados fictícios, exatamente o que cada agente envia: o e-mail, a conversa de
WhatsApp, a planilha e o documento. Eles ficam **dentro da pasta do agente** e são só as peças enviadas, sem moldura de
apresentação. Quem desenha a moldura (cliente de e-mail, celular, claro/escuro) é o **portal de modelos**.

```
agentes/<slug>/                       (no catálogo: .claude/waipe/catalogo/<slug>/)
├── <slug>.md
├── <slug>.json
└── modelos/
    ├── modelos.json                  ← lista das peças (o portal mostra nesta ordem)
    ├── whatsapp-vendedor.html        ← só a conversa
    ├── email-vendedor.html           ← o HTML que o node monta, como é enviado
    ├── consolidado-gestor.html       ← idem
    ├── planilhas/<nome>.html         ← só a planilha
    └── documento/<nome>.pdf
```

Não existe mais galeria nem `index.html` (até a v2 havia `agentes/modelos/` com uma galeria; a v3 tirou).

## Padrão de e-mail Waipe (obrigatório)

Todo e-mail HTML de agente segue o desenho do consolidado do **Guardião da Amostra Padrão**: marca "waipe" e empresa no
topo, cartão branco com faixa escura, eyebrow dourado, título, destaque e indicadores em verde-oliva, tabelas claras com
ranking (círculo, barra e seta) e rodapé Londrisoft. É claro e tem modo escuro automático (`prefers-color-scheme`).

- No **node** do flow: copie o bloco de `kit-email-waipe.js` (do `PADRÃO DE E-MAIL WAIPE` ao `FIM DO PADRÃO`) para o node
  `code` que monta o e-mail e use `wpPagina`, `wpKpis`, `wpSecao`, `wpTabela`, `wpBadge`, `wpBarra`, `wpSeta`, `wpBotao`,
  `wpAviso` e `wpTexto`. `wpPagina` devolve o documento HTML completo.
- Não escreva cores nem estilos soltos no node: use as funções do kit. Texto dentro de `wpTexto`/`wpAviso` vai sem `<div>`
  (use `<span style="display:block;">` para quebrar linha), porque o kit monta parágrafos.
- Ao mudar o kit, troque o bloco em todos os nodes que o usam (o bloco é sempre o mesmo, entre os marcadores).
- Referência pronta: os modelos de `.claude/waipe/catalogo/<modelo>/modelos/`.

## Quando gerar

- **Ao fechar a release** de um agente que envia WhatsApp, e-mail, documento ou planilha (skill `waipe-fechar-release`).
  `waipe.py status` mostra `modelos: PENDENTE` quando o agente ainda não tem `modelos/modelos.json`.
- Agente que já tem modelos: refaça só se a release mudou textos, layout ou peças enviadas.
- No catálogo: a skill `waipe-revisar-modelos` gera os modelos de cada modelo novo ou alterado.

## Base: modelos do catálogo

Se o agente nasceu de um modelo do catálogo (`modelo_base` no `.md`), os modelos de comunicação daquele modelo existem em
`.claude/waipe/catalogo/<modelo>/modelos/`: use-os como ponto de partida, trocando os dados fictícios, os textos e as
peças pelo que **este** agente envia.

## O que gerar por agente (só o que o agente de fato envia)

| Se o flow... | Gere | Tipo no modelos.json |
|---|---|---|
| envia WhatsApp (`zapi_send` ou `http_request` na Z-API) | `whatsapp-vendedor.html` (ou `whatsapp-cliente.html`) com `pagina_whatsapp` | `whatsapp` |
| envia e-mail (`gmail_send`) a vendedor ou cliente | `email-vendedor.html` (ou `email-cliente.html`): o HTML do node | `email` |
| envia consolidado ao gestor | `consolidado-gestor.html`: o HTML do node | `email` |
| anexa ou gera documento (PDF) | `documento/<nome>.pdf` | `documento` |
| cria planilha por vendedor | `planilhas/<vendedor>.html` com `pagina_planilha` | `planilha` |

## Como montar

1. **E-mails: rode o próprio node com dados fictícios.** `comum.rodar_node(flow, "Nome do node", entradas)` (ou
   `node rodar-node.mjs <flow.json> "<node>" <entradas.json>`) executa **só o JavaScript do node `code`**, na sua máquina,
   com as entradas que você montar (`items`, as saídas de outros nodes em `node`, `hoje`). Nada é enviado: Gmail, Z-API,
   Data Lab e Google Sheets não rodam. O HTML devolvido é exatamente o que o node manda, então o modelo fica fiel.
   Monte as entradas lendo o código: que campos ele lê de `$node["..."].json` e de `items`.
2. **WhatsApp:** o texto também sai do node (o campo da mensagem). Desenhe com
   `pagina_whatsapp([{texto, doc?, link?}], contato, hora, data, links)`: PDF anexado vira cartão que abre o PDF; link
   de planilha vira cartão de link (`links` aponta a URL do texto para `planilhas/<nome>.html`).
3. **Planilhas:** `pagina_planilha(titulo, colunas, linhas, aba, larguras)`, com as mesmas colunas que o node grava.
4. **Documento em PDF:** monte o HTML do documento como o node monta (o node costuma devolver esse HTML também) e
   imprima com o navegador sem janela. No Windows/WSL, com o Edge:
   `msedge.exe --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=<caminho do .pdf> file:///<caminho do .html>`
   (os arquivos precisam estar numa pasta que o Windows enxergue, `/mnt/c/...`). Sem navegador, avise e pule o PDF.
5. **modelos.json:** `salvar_manifesto(pasta_modelos, pecas)`, na ordem em que o portal deve mostrar: mensagens primeiro,
   depois o consolidado, as planilhas e os documentos. Cada peça:
   - `arquivo`, `tipo` (`email`, `whatsapp`, `planilha`, `documento`), `rotulo` (ex.: "E-mail do vendedor"), `quem`;
   - e-mail: `assunto`, `de` ("Nome <email>"), `para`, `data` (ex.: "seg., 19 out. 07:00");
   - WhatsApp: `contato` (nome no topo da conversa) e `data` (ex.: "SEGUNDA-FEIRA").
6. **Confira:** abra cada peça no navegador sem janela (`--screenshot=<png>`), no claro e no escuro
   (`--blink-settings=preferredColorScheme=1` força o claro) e na largura de celular. Rode `waipe.py validar`.

`exemplo_gerar.py` (nesta pasta) tem um gerador mínimo: copie para a pasta temporária, adapte e rode de lá.

## Dados fictícios (obrigatório)

- Empresa, gestor, vendedores, clientes, telefones, e-mails e valores **inventados**. Nada que identifique o cliente real.
- E-mails em `@exemplo.com.br` (o validador do catálogo recusa outro domínio), telefones como `(11) 90000-0000`,
  empresa "NOME DA EMPRESA" no catálogo e um nome fictício (ex.: "Empresa Exemplo") nos clientes.
- Não copie IDs de relatório, URLs de planilha reais, contatos de dúvidas reais nem nomes de pessoas do cliente.
- O rodapé de marca do produto ("Londrisoft · Londrina, PR") fica, pois é do próprio e-mail.
- Antes de enviar, busque o nome do cliente, e-mails e telefones reais em `agentes/<slug>/modelos/`.

## Modelos do cliente e do catálogo

- No **repositório do cliente**, os modelos mostram o que **aquele cliente** envia, com o layout e os textos dele
  (dados fictícios).
- No **catálogo**, o mesmo agente fica genérico: dados descaracterizados ("NOME DA EMPRESA") e e-mails no padrão Waipe.

## Enviar

`git add agentes/<slug>/modelos`, commit `docs(<slug>): modelos de comunicação` e `waipe.py salvar`. Depois siga com a
release do agente.
