# Framework de agentes Waipe

Modelo para versionar os flows (agentes) do Waipe Flow de cada cliente, com uma IA (Claude Code) que cria os
agentes a partir de um catálogo de modelos e cuida das versões.

## Ideia

- **Um repositório por cliente**, criado a partir do template `waipe-agentes-template`.
- **Cada agente** = uma pasta `agentes/<slug>/` com o `<slug>.json` (para importar no Waipe Flow) e o `<slug>.md`
  (o que faz, como configurar, como testar, versão e histórico).
- **Catálogo**: modelos anônimos de agentes dentro do framework. Ao pedir um agente novo, a IA procura um modelo
  parecido, sugere e pergunta só o que falta.
- **Branch única (`main`)**: toda alteração vai para a `main` (validada) e você testa a partir dela. Quando achar
  bom, pede "fecha a release do X": a IA cria a tag `<slug>/vX.Y.Z` e um Release com os arquivos do agente
  anexados. As versões antigas ficam na aba Releases para baixar quando precisar.
- **Framework atualizável**: tudo do framework fica em caminhos próprios (abaixo). `waipe atualizar` troca só eles;
  `agentes/`, `CLAUDE.md` e `README.md` do cliente nunca são tocados.

## Estrutura

```
<repo do cliente>/
├── CLAUDE.md                     ← do cliente: nome e particularidades (ERP, destinatários, pegadinhas)
├── README.md                     ← do cliente
├── agentes/                      ← do cliente: um agente por pasta
│   └── clientes-inativos/
│       ├── clientes-inativos.json
│       └── clientes-inativos.md
├── .claude/
│   ├── settings.json             ← framework: permissões e hook que valida a cada edição
│   ├── settings.local.json       ← seu, fora do git
│   ├── rules/waipe-*.md          ← framework: regras e fluxo de trabalho (carregadas sozinhas)
│   ├── skills/waipe-*/           ← framework: o que a IA sabe fazer (abaixo)
│   ├── agents/waipe-flow.md      ← framework: subagente gerador de JSON
│   └── waipe/                    ← framework: VERSION, CHANGELOG, waipe.py, modelo-agente.md, catalogo/
└── .github/workflows/waipe-validar.yml   ← framework: CI valida todo push na main
```

## O que pedir para a IA

| Você diz | Skill | O que acontece |
|---|---|---|
| "quero criar um agente de X" / "altera o agente Y" | `waipe-criar-agente` | busca no catálogo, pergunta, gera JSON + MD, envia para a main para você testar |
| "fecha a release do X" | `waipe-fechar-release` | fecha a versão do agente: tag e Release com os arquivos |
| "atualiza o framework" | `waipe-atualizar-framework` | troca só os arquivos do framework pela versão nova |
| (no template) "revisa os modelos" | `waipe-revisar-modelos` | lê os agentes publicados nos clientes, propõe modelos novos, publica o framework |
| (no template) "novo cliente X" | `waipe-novo-cliente` | cria o repositório do cliente a partir do template |
| qualquer dúvida de node/JSON | `waipe-flow` | guia completo dos 21 nodes e princípios de flow |

## Comandos (`python3 .claude/waipe/waipe.py ...`)

| Comando | Faz |
|---|---|
| `status` | versão do framework; versão em trabalho e publicada de cada agente; modelos do catálogo |
| `validar [pasta]` | regras de importação do Waipe Flow (gatilho único, tipos, handles, DAG, blocklist, credenciais) + `.md` |
| `novo-agente <slug>` | cria `agentes/<slug>/` com o `.md` do modelo |
| `salvar` | valida e envia para a `main` o que já foi commitado |
| `release <slug> <nivel>` | fecha a versão (`patch`, `minor`, `major` ou `X.Y.Z`): tag `<slug>/vX.Y.Z` e Release com os arquivos da pasta |
| `atualizar [vX.Y.Z]` | framework do template para este cliente (padrão: última versão) |
| `migrar` | uma vez, ao sair do gitflow antigo: apaga `develop` e deixa só a `main` |
| `iniciar "<Nome>"` | prepara um repositório recém-criado do template |
| `release-framework <nivel>` | (template) fecha a versão do framework: CHANGELOG, VERSION, tag `vX.Y.Z` |
| `novo-cliente <repo> "<Nome>"` | (template) cria o repositório do cliente |
| `clientes` | (template) lista os repositórios com o tópico `waipe-cliente` |

Requisitos: Python 3.12+, git e gh autenticado na conta dona dos repositórios.

## Ciclo semanal

1. Durante a semana, agentes novos são criados e publicados nos clientes.
2. No template: "revisa os modelos". A IA traz o que foi publicado, você escolhe o que vira modelo, ela anonimiza,
   publica uma versão nova do framework e oferece atualizar todos os clientes.
