# Modelos de comunicação dos agentes (padrão)

Para cada agente que **envia algo a alguém** (WhatsApp, e-mail, documento, planilha), o repositório guarda **modelos
navegáveis** do que é enviado, com dados fictícios, para apresentação e para o usuário ver como chega. Ficam em
`agentes/modelos/<slug>/`, com um `index.html` que reúne todos os fluxos.

> `agentes/modelos/` **não é um agente**: é pasta reservada. O `waipe.py` ignora essa pasta em `validar`, `status`,
> `novo-agente` e `release`.

## Quando gerar

- **Ao fechar a release de um agente** que envia mensagem, e-mail, documento ou planilha (skill `waipe-fechar-release`),
  **antes** de rodar `waipe.py release`. O `waipe.py status` mostra `modelos: PENDENTE` para o agente que ainda não tem.
- Agente que já tem modelos: refaça **só** se a release mudou o texto, o layout ou as peças enviadas. Se nada disso mudou,
  não mexa.
- Agente que não envia nada a terceiros (só grava planilha interna, por exemplo): não precisa de modelos.

## Regra de ouro: se `agentes/modelos/` já existe, apenas ACRESCENTE

- Nunca recrie a pasta, o `index.html` nem os modelos dos outros fluxos.
- Crie só `agentes/modelos/<slug>/` do agente novo e **acrescente o cartão dele** no `index.html`
  (`atualizar_indice` faz exatamente isso e troca o cartão se o agente já estava lá).
- Se `agentes/modelos/` não existe, `atualizar_indice` cria a pasta, o `index.html` e o `README.md`.

## O que gerar por agente (só o que o agente de fato envia)

| Se o flow... | Gere | Observação |
|---|---|---|
| envia WhatsApp (`zapi_send` ou `http_request` na Z-API) ao vendedor/cliente | `whatsapp-vendedor.html` (ou `whatsapp-cliente.html`) | Conversa interativa, texto igual ao do node. Com documento anexado, o PDF aparece como anexo e abre dentro da conversa. Com link, aparece o cartão do link. |
| envia e-mail (`gmail_send`) ao vendedor/cliente | `email-vendedor.html` (ou `email-cliente.html`) | HTML igual ao do node, dentro de um visualizador com Computador/Celular. |
| anexa ou gera documento (PDF) | `documento/<nome>.pdf` | Vira anexo na tela de WhatsApp (parâmetro `doc`). |
| envia consolidado ao gestor | `consolidado-gestor.html` | Mesmo visualizador de e-mail. |
| cria planilha por vendedor | `planilhas/<vendedor>.html` | Aparência de planilha. Os botões/links do consolidado e do WhatsApp apontam para elas. |

Se o agente não manda mensagem ao vendedor (só ao gestor, por exemplo), gere só o que existe e diga isso na `nota` do
cartão do índice.

## Como montar (sem rodar o flow)

1. Leia o `.json` do agente e **entenda** o código dos nodes `code` que montam textos e HTML (WhatsApp, e-mail,
   documento, consolidado). **Não execute os nodes** nem chame os relatórios do Data Lab: o modelo é escrito à mão.
2. Copie `exemplo_gerar.py` (nesta pasta) para a pasta temporária, adapte e rode de lá. Ele usa `comum.py`, que traz:
   - `pagina_whatsapp(...)`: conversa interativa (digitando, repetir, claro/escuro, anexo PDF com abertura, cartão de link);
   - `pagina_email(..., celular=True)`: visualizador de e-mail; se o HTML tiver `@media (prefers-color-scheme: dark)`, as
     versões clara e escura seguem o botão claro/escuro;
   - `pagina_planilha(...)`: planilha no estilo Google Sheets;
   - `card(...)` e `atualizar_indice(...)`: cartão e índice.
3. Reproduza o **layout e os textos do node** (mesma ordem, mesmos rótulos, mesmas cores), trocando os dados por fictícios.
   O e-mail tem de ser fiel ao que o node gera; só os dados mudam.
4. **Documento em PDF:** monte o HTML do documento como o node monta (margem de página com `@page{size:A4;margin:20mm 18mm}`)
   e imprima com o navegador sem janela. No Windows/WSL, com o Edge:
   `msedge.exe --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=<caminho do .pdf> file:///<caminho do .html>`
   (com Chrome é igual). Os arquivos precisam estar em uma pasta que o Windows enxergue (`/mnt/c/...`). Sem navegador
   disponível, entregue o documento em HTML e avise.
5. Confira o resultado: abra as páginas com o navegador sem janela (`--screenshot=<png>`) e olhe as imagens; para o
   WhatsApp use `--virtual-time-budget=9000` (a conversa é animada). Teste também a largura de celular nos e-mails.

## Dados fictícios (obrigatório)

- Empresa, gestor, vendedores, clientes, telefones, e-mails e valores **inventados**. Nada que identifique o cliente real.
- E-mails em `@exemplo.com.br`, telefones como `(11) 90000-0000`, empresa tipo "Doce Vale" / "Empresa Exemplo".
- Não copie IDs de relatório, URLs de planilha reais, contatos de dúvidas reais nem nomes de pessoas do cliente.
- O rodapé de marca do produto ("Londrisoft · Londrina, PR") pode ficar, pois é do próprio e-mail.
- Rode uma busca por nome do cliente, e-mails e telefones reais na pasta `agentes/modelos/` antes de enviar.

## Cartão do índice

`card(nome, icone, frequencia, quem, resumo, pasta, pecas, nota)`:
- `frequencia`: uma frase (ex.: "Toda segunda e quinta, 07:00");
- `quem`: quem recebe (ex.: "Cada vendedor e o gestor comercial");
- `resumo`: uma linha do que é enviado;
- `pecas`: lista de `(emoji, rótulo, arquivo dentro da pasta do agente)`;
- `nota`: opcional, para avisos (ex.: "Este fluxo não envia mensagem aos vendedores").

## Enviar

`git add agentes/modelos`, commit `docs(<slug>): modelos de comunicação` e `waipe.py salvar`. Depois siga com a release do
agente. Os modelos não são anexados ao Release (ele leva só os arquivos de `agentes/<slug>/`).
