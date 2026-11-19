---
name: waipe-criar-plugin
description: Cria uma página nova (plugin .json do Waipe Páginas) ou altera um plugin existente, do pedido até a release. Use quando o usuário pedir "nova página de X", "plugin de Y", "muda a página Z", "a coluna não bateu", "acrescenta um indicador", "troca o filtro" ou qualquer ajuste numa página do Waipe Páginas.
---

# Criar ou alterar um plugin

Resultado: `plugins/<slug>/<slug>.json` + `<slug>.md` + `exemplo.json` (no template: `modelos/plugins/<slug>/`),
validados com o motor, enviados para a `main` e com **release fechada** no fim (com a prévia para o simulador).
Ferramenta: `python3 .claude/waipe/plugins.py` (abaixo, `plugins`). Regras: `waipe-plugins.md`.

## 1. Entender e buscar parecido

1. Resuma o pedido numa frase: plugin **novo** ou **alteração** (`plugins status`)? É mesmo de plugin, ou pede algo
   que a plataforma não tem (bloco novo, função nova, mudança de visual, menu, login, modo administrador)? Se for de
   plataforma, diga ao usuário que é **coisa da plataforma** e siga a regra 2 de `waipe-plugins.md` (faz no
   `waipe-paginas`, com release lá, e só depois usa aqui).
2. Carregue a skill `waipe-plugin-formato` (o que o motor oferece) antes de desenhar.
3. Confira que o `waipe-paginas` está ao lado (`../waipe-paginas`) e atualizado (`git -C ../waipe-paginas pull`); sem
   ele não há validação completa nem prévia.
4. Rode `plugins catalogo <palavras>` (catálogo `modelos/plugins/` e plugins do cliente) e leia o `.md` dos
   candidatos. Sugira até 3 como base (o que cada um faz e o que mudaria) e deixe o usuário decidir
   (AskUserQuestion). Nenhum combina: diga e siga do zero.

## 2. Perguntar só o necessário

No máximo 4 perguntas por rodada, com opções concretas. Comece pelas "Perguntas para personalizar" do plugin base e
complete com: o relatório do Data Lab (colunas e período), a regra (situações, cortes, o que excluir), as telas
(KPIs, blocos, colunas, filtros, ordem) e o que vai em Configurações. Não pergunte o que o modelo já responde.

## 3. Aprovar o desenho

Mostre antes de gerar: colunas do Data Lab → campos, passos do cálculo, situações (ícone, regra), KPIs e blocos de
cada tela, parâmetros, campos do banco. Para alteração, o que muda e o nível da versão. Espere o ok.

## 4. Gerar

1. Novo: `plugins novo <slug> --modelo <base>` (ou sem `--modelo`). Alteração: edite os arquivos da pasta.
2. Edite o `.json` (formato em `waipe-plugin-formato`). Use só o que existe no motor. Mantenha a seção `banco` em dia:
   campo novo que as telas leem entra em `campos`; renomear, apagar ou mudar tipo leva o passo em `banco.migracoes`.
3. `exemplo.json`: linhas fictícias com os **nomes de coluna que o Data Lab devolve** (`cliente_fornecedor`,
   `lancamento`, `estoque_total`...), cobrindo todas as situações (é a base da validação e da prévia).
4. `.md`: todas as seções do modelo (`.claude/waipe/modelo-plugin.md`); Relatório do Data Lab igual ao `dataLab.texto`;
   uma linha por mudança em `### Não publicado`. Não mexa em `versao` (a release muda).
5. `plugins validar plugins/<slug>` até passar. Para ver como fica: `plugins gerar-modelos <slug>` e abra
   `plugins/<slug>/modelos/painel.html`.

## 5. Enviar, testar e fechar a release

1. Commit `feat(<slug>): ...` / `fix(<slug>): ...` e `python3 .claude/waipe/waipe.py salvar`.
2. Diga ao usuário como testar: em Configurações gerais > Páginas, "Instalar ou atualizar página (.json)"; a tela
   mostra a versão atual e a nova e o que muda no banco (confira antes de confirmar); escolher o menu; seguir a aba
   Configurações > Integração da página; Atualizar agora e conferir as colunas com ✓.
3. Feche a release (skill `waipe-fechar-release-plugin`) ao fim da tarefa, a não ser que o usuário peça para esperar.
