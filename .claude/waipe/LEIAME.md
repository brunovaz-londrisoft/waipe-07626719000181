# Framework Waipe (agentes e plugins)

Base dos repositórios de cliente da Waipe: os **agentes** (flows do Waipe Flow) e as **páginas** (plugins do Waipe
Páginas) de cada cliente, com uma IA (Claude Code) que cria os dois a partir de um catálogo de modelos, gera os
exemplos para o simulador e cuida das versões. Template: `brunovaz-londrisoft/waipe-template`.

## Ideia

- **Um repositório por cliente** (`waipe-<cnpj>`), criado a partir deste template. Nele ficam os **agentes** do cliente
  (flows do Waipe Flow, em `agentes/`) e as **páginas** do cliente (plugins do Waipe Páginas, em `plugins/`).
- **Cada agente** = `agentes/<slug>/` com o `.json` (importar no Waipe Flow) e o `.md` (o que faz, como configurar,
  versão e histórico). **Cada página** = `plugins/<slug>/` com o `.json` (instalar no Waipe Páginas), o `.md` e o
  `exemplo.json` (dados fictícios).
- **Catálogo**: modelos anônimos de agentes (`modelos/agentes/`) e de plugins (`modelos/plugins/`). Ao pedir algo
  novo, a IA procura o modelo mais parecido, sugere e pergunta só o que falta.
- **Simulador**: agentes e plugins geram as suas peças de exemplo em `<pasta>/modelos/` (e-mail, WhatsApp, planilha;
  painel e relatório da página), listadas no `modelos.json`. O [portal de modelos](https://github.com/brunovaz-londrisoft/portal-modelos-waipe)
  mostra o catálogo e os repositórios dos clientes com essas peças.
- **Branch única (`main`)**: toda alteração vai para a `main` (validada) e você testa a partir dela. Fechar versão
  cria a tag e um Release com os arquivos anexados: agente `<slug>/vX.Y.Z`, página `plugins/<slug>/vX.Y.Z`.
- **Framework atualizável**: tudo do framework fica em caminhos próprios (`.claude/waipe`, regras, skills, `modelos/`,
  CI). `waipe.py atualizar` troca só eles; `agentes/`, `plugins/`, `CLAUDE.md` e `README.md` do cliente nunca são tocados.
- **Plataforma das páginas**: o [`waipe-paginas`](https://github.com/brunovaz-londrisoft/waipe-paginas) (motor,
  componentes, banco, Vercel) fica em outro repositório e não tem plugin. Tenha um clone dele ao lado deste repositório
  (`../waipe-paginas`) para a validação completa e as prévias dos plugins.

## Estrutura

Agentes e plugins ficam **separados por pasta**, cada um com o seu `.md` de instruções, e o catálogo de modelos dos
dois fica junto em `modelos/`:

```
waipe-<cnpj>/  (ou o template)
├── CLAUDE.md                     ← do cliente: nome e particularidades (ERP, destinatários, pegadinhas)
├── README.md                     ← do cliente
├── agentes/                      ← do cliente: um agente (flow do Waipe Flow) por pasta
│   └── <slug>/
│       ├── <slug>.json           ← para importar no Waipe Flow
│       ├── <slug>.md             ← o que faz, como configurar, versão e histórico
│       └── modelos/              ← e-mails, WhatsApp, planilhas fictícios + modelos.json (simulador do portal)
├── plugins/                      ← do cliente: uma página (plugin do Waipe Páginas) por pasta
│   └── <slug>/
│       ├── <slug>.json           ← para instalar em Configurações gerais > Páginas
│       ├── <slug>.md             ← o que mostra, Data Lab, banco, configurações, versão e histórico
│       ├── exemplo.json          ← linhas fictícias do Data Lab (validação e prévia)
│       └── modelos/              ← prévia do painel e do relatório + modelos.json (simulador do portal)
├── modelos/                      ← framework: catálogo (ponto de partida para criar)
│   ├── agentes/<slug>/           ← modelos de agentes anonimizados, INDICE.md, rotina de revisão
│   └── plugins/<slug>/           ← modelos de plugins (páginas) com exemplo fictício
├── .claude/
│   ├── settings.json             ← framework: permissões e hooks que validam a cada edição
│   ├── settings.local.json       ← seu, fora do git
│   ├── rules/waipe-*.md          ← framework: regras de agentes e de plugins (carregadas sozinhas)
│   ├── skills/waipe-*/           ← framework: o que a IA sabe fazer (abaixo)
│   ├── agents/waipe-flow.md      ← framework: subagente gerador de JSON de flow
│   └── waipe/                    ← framework: VERSION, CHANGELOG, waipe.py (agentes), plugins.py (plugins),
│                                    modelo-agente.md, modelo-plugin.md, plugin/ (validar.mjs, previa.mjs),
│                                    modelos-comunicacao/ (kit de e-mail e padrão das peças)
└── .github/workflows/waipe-validar.yml   ← framework: CI valida agentes e plugins a cada push na main
```

## O que pedir para a IA

| Você diz | Skill | O que acontece |
|---|---|---|
| "quero criar um agente de X" / "altera o agente Y" | `waipe-criar-agente` | busca no catálogo, pergunta, gera JSON + MD, envia para a main para você testar |
| "fecha a release do X" (agente) | `waipe-fechar-release` | cria os modelos de comunicação (`agentes/X/modelos/`) e fecha a versão: tag e Release |
| "quero uma página de X" / "muda a página Y" | `waipe-criar-plugin` | busca no catálogo, pergunta, gera o plugin (.json, .md, exemplo), valida com o motor e envia |
| "fecha a versão da página X" | `waipe-fechar-release-plugin` | gera a prévia para o simulador e fecha a versão: tag `plugins/X/vX.Y.Z` e Release |
| dúvida sobre blocos, fórmulas, banco das páginas | `waipe-plugin-formato` | tudo o que o motor do Waipe Páginas oferece |
| qualquer dúvida de node/JSON de flow | `waipe-flow` | guia completo dos 21 nodes e princípios de flow |
| "atualiza o framework" | `waipe-atualizar-framework` | troca só os arquivos do framework (e o catálogo) pela versão nova |
| (no template) "revisa os modelos" | `waipe-revisar-modelos` | lê agentes e plugins publicados nos clientes, propõe modelos novos, publica o framework |
| (no template) "novo cliente X" | `waipe-novo-cliente` | cria o repositório `waipe-<cnpj>` a partir do template |

## Comandos

Agentes (`python3 .claude/waipe/waipe.py ...`):

| Comando | Faz |
|---|---|
| `status` | versão do framework; versão em trabalho e publicada de cada agente; modelos do catálogo |
| `validar [pasta]` | agentes (regras de importação do Waipe Flow + `.md`) e, sem pasta, também os plugins |
| `catalogo [termos]` | procura no catálogo um modelo de agente parecido |
| `novo-agente <slug> [--modelo <m>]` | cria `agentes/<slug>/` em branco ou a partir de um modelo |
| `salvar` | valida agentes e plugins e envia para a `main` o que já foi commitado |
| `release <slug> <nivel>` | fecha a versão do agente: tag `<slug>/vX.Y.Z` e Release com os arquivos da pasta |
| `atualizar [vX.Y.Z] [--forcar]` | traz o framework do template para este cliente (padrão: última versão) |
| `iniciar "<Nome>"` | prepara um repositório recém-criado do template |
| `release-framework <nivel>` | (template) fecha a versão do framework: CHANGELOG, VERSION, tag `vX.Y.Z` |
| `novo-cliente <repo> "<Nome>"` | (template) cria o repositório do cliente |
| `clientes` | (template) lista os repositórios de cliente |

Plugins (`python3 .claude/waipe/plugins.py ...`):

| Comando | Faz |
|---|---|
| `status` | cada plugin do cliente: última release e se mudou desde então |
| `validar [pasta]` | estrutura, par `.json` + `.md`, exemplo e, com o `waipe-paginas` ao lado, o motor completo |
| `catalogo [termos]` | procura um plugin parecido (catálogo e plugins do cliente) |
| `novo <slug> [--modelo <m>]` | cria `plugins/<slug>/` (no template, `modelos/plugins/<slug>/`) |
| `gerar-modelos [slug]` | prévia do painel e do relatório para o simulador (`<pasta>/modelos/`) |
| `release <slug> <nivel>` | fecha a versão da página: prévias, tag `plugins/<slug>/vX.Y.Z` e Release |

Requisitos: Python 3.12+, Node 22+, git, gh autenticado na conta dona dos repositórios e, para plugins, o
`waipe-paginas` clonado ao lado.

## Ciclo semanal

1. Durante a semana, agentes e páginas novos são criados e publicados nos clientes.
2. No template: "revisa os modelos". A IA traz o que foi publicado, você escolhe o que vira modelo, ela anonimiza,
   publica uma versão nova do framework e oferece atualizar todos os clientes.
