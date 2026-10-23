# Rotina de atualização dos modelos do catálogo

Esta rotina diz à IA como manter o catálogo em dia com os agentes que existem nos repositórios dos clientes. É seguida
pela skill `waipe-revisar-modelos` (pedidos como "revisa os modelos", "atualiza o catálogo", "revisão semanal").

**Regras fixas**

- O catálogo existe **só no template principal** (`brunovaz-londrisoft/waipe-agentes-template`). Nunca crie catálogo
  nem modelos em repositório de cliente ou em repositório compartilhado (fork do template de outra conta).
- **Nada muda em produção nos clientes**: os flows (`agentes/<slug>/<slug>.json`) dos clientes são só leitura nesta rotina.
- **Fontes**: todos os repositórios `waipe-*` com o framework que a conta enxerga: os próprios, os de organizações e os
  **compartilhados** com ela (`waipe.py clientes`). Repositório novo entra sozinho na próxima rodada.
- Agente em rascunho (`versao: 0.0.0`) fica de fora até ter release.

## 1. Comparar (nome e fluxo)

```
python3 .claude/waipe/waipe.py comparar-catalogo          # tabela
python3 .claude/waipe/waipe.py comparar-catalogo --json   # para a IA ler
```

O comando compara cada agente publicado com **todos** os modelos do catálogo pelo nome e pela **estrutura do fluxo**:
quantos nodes de cada tipo e como eles se ligam (tipo → saída → tipo). A similaridade vai de 0 a 100% (40% tipos de node,
60% ligações). A partir de **85%** é o mesmo fluxo. Não decida só pelo nome: dois agentes com o mesmo nome podem fazer
coisas diferentes, e o mesmo fluxo pode estar com outro nome.

Cada modelo guarda em `catalogo/<slug>/origem.json` o fluxo dos agentes que lhe deram origem (o repositório fica só como
um código, sem o nome do cliente). Por isso o agente de origem continua reconhecido mesmo depois de o modelo ser adaptado
(node "Montar E-mail", correções), e um agente de outro cliente igual ao original também é achado.

| Situação | O que significa | O que fazer |
|---|---|---|
| `no catálogo` | é a origem de um modelo, ou mesmo nome e mesmo fluxo | Compare a versão do cliente com a que deu origem ao modelo (ver `REVISOES.md`). Release mais nova no cliente: leia o diff (`gh release download`/`git show`) e, se for melhoria que serve a outros clientes, faça a **melhoria do modelo** (sobe a `versao` do modelo). |
| `mesmo nome, fluxo diferente` | mesmo nome, mas o fluxo é outro | **Modelo novo** com o próximo número livre: slug `<slug>-2` e nome "<Nome> (2)", depois `-3` "(3)" e assim por diante. O comando já sugere o número. |
| `fluxo parecido` | fluxo de um modelo existente com outro nome | Avalie se é o mesmo agente renomeado (trate como `no catálogo` do modelo parecido) ou variação que merece modelo próprio. |
| `novo` | não há modelo com esse fluxo | **Modelo novo**, se o padrão servir a outros clientes. Se for específico de um cliente (regra que só faz sentido para ele), não entra: registre o motivo em `REVISOES.md`. |
| `rascunho` | sem release | Fica de fora. |

## 2. Escolher

A IA escolhe sozinha os agentes **que ainda não existem** no catálogo (`novo` e `mesmo nome, fluxo diferente`) e que
sirvam a outros clientes, e os traz para o catálogo. Melhorias de modelo existente e casos de dúvida (`fluxo parecido`,
agente que parece específico) vão numa tabela para o usuário decidir: cliente, agente, versão, situação, similaridade,
decisão proposta e motivo.

## 3. Trazer para o catálogo

Para cada modelo escolhido, na `main` do template:

1. **Baixar** o `.json` e o `.md` da `main` do cliente (`gh api repos/<repo>/contents/agentes/<slug>/<slug>.json`)
   numa pasta temporária. Nada é escrito no repositório do cliente.
2. **Descaracterizar** os dados do cliente:
   - destinos de e-mail e telefone viram exemplo (`gestor@exemplo.com`) ou a expressão do contato real (`{{ $json.email }}`);
   - IDs de relatório do Data Lab, planilhas, pastas e documentos viram `SUBSTITUA_PELO_...`; chaves e tokens de API
     (cabeçalhos, URLs) viram `SUBSTITUA_PELA_CHAVE_...`; `credentialId` fica `""`;
   - nome da empresa, de pessoas, vendedores, tabelas e redes do cliente saem dos textos, comentários e `CONFIG`
     (`NOME DA EMPRESA`, "Tabela de Comissão");
   - posições dos nodes arredondadas (coordenada longa parece CNPJ para o validador);
   - o **texto (prompt) dos relatórios do Data Lab fica** no `.md`, sem o ID.
3. **Corrigir** os problemas conhecidos que o `.md` do cliente aponta (node solto, loop sem entrada, `RAW` em vez de
   `USER_ENTERED` etc.) e registrar no Histórico do modelo.
4. **E-mails no padrão Waipe** (`.claude/waipe/modelos-comunicacao/kit-email-waipe.js`), com o mesmo conteúdo do cliente:
   - e-mail montado num node `code` com outro desenho: reescreva a parte visual com as funções do kit (os cálculos ficam);
   - HTML escrito direto no `body` do `gmail_send`: crie um node `code` "Montar E-mail ..." com o kit logo antes do envio
     e deixe o `gmail_send` com `{{ $json.assunto }}` e `{{ $json.corpo_html }}`;
   - o node de processamento devolve **dados** (listas, totais), não HTML colorido; cores só pelo kit.
5. **`.md` do modelo**: segue o modelo de agente e tem `## Quando usar` e `## Perguntas para personalizar`; cabeçalho com
   `icone`, `resumo`, `frequencia`, `quem_recebe` (e `nota`, se houver), que o portal de modelos mostra; Histórico
   `### v1.0.0 (data)` dizendo de que agente veio (cliente piloto anônimo e versão) e o que mudou.
6. **Modelos de comunicação**: escreva `catalogo/<slug>/gerar_modelos.py` com os dados fictícios embutidos (use os
   existentes como exemplo) e rode `python3 .claude/waipe/waipe.py gerar-modelos <slug>`. O gerador roda só o JavaScript dos
   nodes `code` (`rodar_node`): nada é enviado. Confira as peças no navegador sem janela, no claro e no escuro.
7. **Registrar a origem**: `python3 .claude/waipe/waipe.py registrar-origem <modelo> <dono/repo> <agente>` grava o fluxo
   do agente do cliente em `catalogo/<modelo>/origem.json` (refaça ao adotar uma melhoria de outra versão).
8. **Registrar no catálogo**: linha na tabela de `INDICE.md` e do `README.md` (Modelos prontos), linha em `REVISOES.md` (data,
   cliente piloto anônimo, tag vista, decisão) e em `## Não publicado` do `.claude/waipe/CHANGELOG.md`.
9. **Validar e publicar**: `waipe.py validar` até passar (barra CNPJ e e-mail real no catálogo), commit, `waipe.py salvar`,
   `waipe.py release-framework minor` e atualizar os clientes (skill `waipe-atualizar-framework`, seção do template).

## Quando o kit de e-mail mudar

```
python3 .claude/waipe/waipe.py atualizar-kit   # troca o bloco do kit em todos os nodes do catálogo
python3 .claude/waipe/waipe.py gerar-modelos   # regera as peças de todos os modelos
```

Os flows de produção dos clientes não são tocados: cada cliente recebe o kit novo quando o agente dele for alterado.
