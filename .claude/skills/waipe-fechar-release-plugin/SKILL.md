---
name: waipe-fechar-release-plugin
description: Fecha a versão de um plugin do Waipe Páginas (prévia para o simulador, tag plugins/<slug>/vX.Y.Z e GitHub Release com o .json, o .md, o exemplo e as prévias). Use ao fim de toda mudança em plugin, ou quando o usuário disser "fecha a versão da página X", "publica o plugin", "gera release do plugin".
---

# Fechar a release de um plugin

1. `python3 .claude/waipe/plugins.py status` mostra cada plugin, a última release e se mudou desde então.
2. Nível (se o usuário não disse): leia `### Não publicado` no `.md`. patch = correção, minor = comportamento novo
   (inclui campo novo no banco), major = muda o relatório do Data Lab, a chave, o slug ou renomeia/apaga/muda tipo de
   campo do banco. Diga qual escolheu.
3. Confira que `### Não publicado` descreve tudo desde a última tag
   (`git diff plugins/<slug>/vX.Y.Z -- plugins/<slug>`).
4. Tenha o `waipe-paginas` ao lado e atualizado: a release roda a validação completa e gera a prévia com o motor.
5. `python3 .claude/waipe/plugins.py release <slug> <nivel>`: grava `versao` no `.json` e no `.md`, fecha o
   histórico, gera `plugins/<slug>/modelos/` (painel.html, relatorio.html, modelos.json: o simulador do portal de
   modelos mostra), cria a tag `plugins/<slug>/vX.Y.Z` e o Release com os arquivos da pasta.
6. **No template** (plugin do catálogo em `modelos/plugins/`): o mesmo comando só grava versão, histórico e prévia e faz
   o commit; escreva a linha em `## Não publicado` do `.claude/waipe/CHANGELOG.md` e publique com
   `waipe.py release-framework <nivel>`.
7. Responda com a tag, o link do Release, o que entrou e a versão mínima da plataforma.
