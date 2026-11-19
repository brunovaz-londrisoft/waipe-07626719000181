# Fluxo de trabalho dos plugins (gerado pelo framework, não edite no repositório do cliente)

```
main ──alterar, commit, salvar──► instalar o .json no Waipe Páginas e testar ──► release <slug> ──► prévias + tag plugins/<slug>/vX.Y.Z + GitHub Release
```

| Passo | Comando (`python3 .claude/waipe/plugins.py ...`) | Quem dispara |
|---|---|---|
| Procurar parecido | `catalogo <palavras>` | sempre, antes de criar |
| Plugin novo | `novo <slug> [--modelo <plugin>]` | skill `waipe-criar-plugin` |
| Conferir | `validar [plugins/<slug>]` (o hook valida a cada edição) | sempre |
| Enviar | commit `tipo(slug): resumo` + `waipe.py salvar` | quem mudou |
| Prévia do simulador | `gerar-modelos [slug]` (a release já gera) | quando quiser ver antes |
| Fechar versão do plugin | `release <slug> <patch\|minor\|major>` | skill `waipe-fechar-release-plugin`, ao fim de toda mudança |

- A validação completa e a prévia usam o motor do `waipe-paginas` (pasta irmã `../waipe-paginas` ou variável
  `WAIPE_PAGINAS`). Sem ele, só a parte estrutural roda e a prévia não sai: antes de release, tenha o `waipe-paginas`
  ao lado e atualizado (`git pull`).
- Versões antigas: aba Releases ou `git show plugins/<slug>/vX.Y.Z:plugins/<slug>/<slug>.json`.
- O `.md` diz a versão mínima da plataforma (`plataforma`). Plugin que usa recurso novo da plataforma sobe esse número.
- No template, plugins novos ou melhorados vão para `modelos/plugins/` e saem na release do framework
  (`waipe.py release-framework`), como os modelos de agente.
