# Fluxo de trabalho dos agentes (gerado pelo framework, não edite no repositório do cliente)

```
main (branch única) ──alterar, commit, salvar──► usuário importa e testa ──"fecha a release de X"──► tag <slug>/vX.Y.Z + GitHub Release
```

Decisão do dono do framework (v2.0.0): **uma branch só, `main`**. Não existem `develop`, `feature/` nem PR.

- **Dia a dia**: altere os arquivos, faça commit na `main` (`tipo(slug): resumo`) e rode `waipe.py salvar`, que
  valida e envia para o GitHub. O usuário importa o JSON da `main` no Waipe Flow e testa. Vale para qualquer
  mudança: JSON de flow, `.md`, `CLAUDE.md`, `README.md`.
- **Histórico em andamento**: cada mudança num agente ganha uma linha na seção `### Não publicado` do topo do
  `## Histórico` do `.md` dele (crie a seção se não existir). Não mexa em `versao` no dia a dia: ela é a da última
  release.
- **Fechar release**: só quando o usuário pedir ("fecha a release do X", "fecha a versão"). É **por agente**:
  `waipe.py release <slug> <patch|minor|major|X.Y.Z>`. O script troca `### Não publicado` por
  `### vX.Y.Z (data)`, atualiza `versao` e `atualizado`, faz commit e push, cria a tag `<slug>/vX.Y.Z` e um
  GitHub Release com **todos os arquivos da pasta** `agentes/<slug>/` anexados (inclusive flows auxiliares).
- **Versões antigas**: ficam na aba Releases (baixar os anexos) ou pela tag:
  `git show <slug>/vX.Y.Z:agentes/<slug>/<slug>.json`.
- **Nível da versão** (se o usuário não disser): patch = correção, minor = comportamento novo, major = muda
  credenciais, gatilho, saída ou quem recebe. Proponha o nível e siga.

| Passo | Comando | Quem dispara |
|---|---|---|
| Agente novo | `waipe.py novo-agente <slug>` | skill `waipe-criar-agente` |
| Enviar alteração para teste | commit na `main` + `waipe.py salvar` | quem fez a mudança, sempre |
| Fechar versão de um agente | `waipe.py release <slug> <nivel>` | skill `waipe-fechar-release`, só a pedido do usuário (cria antes os modelos de comunicação em `agentes/modelos/<slug>/`) |
| Atualizar o framework | `waipe.py atualizar [vX.Y.Z]` | skill `waipe-atualizar-framework` |
| Sair do gitflow antigo | `waipe.py migrar` (uma vez) | skill `waipe-atualizar-framework` |

## Repositório template (o próprio framework)

Vale só em `brunovaz-londrisoft/waipe-agentes-template`:

- `agentes/` fica vazio. O trabalho é no framework: `.claude/`, `.github/`, `README.md`, `CLAUDE.md`.
- Mesma branch única: commit na `main` e `salvar`. Cada mudança ganha uma linha em `## Não publicado` no topo do
  `.claude/waipe/CHANGELOG.md`.
- Para os clientes receberem: `waipe.py release-framework <patch|minor|major>` (maior = cliente precisa agir). O
  script fecha o CHANGELOG, sobe a `VERSION`, cria a tag `vX.Y.Z` e o Release. Feche a versão logo depois de
  mudanças no framework, a não ser que o usuário peça para esperar.
- Novos modelos de catálogo vêm da skill `waipe-revisar-modelos`. Novos clientes, da skill `waipe-novo-cliente`.
- O `CLAUDE.md` e o `README.md` do template viram ponto de partida dos clientes: mude-os com cuidado.
