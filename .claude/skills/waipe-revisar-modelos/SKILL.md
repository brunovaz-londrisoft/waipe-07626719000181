---
name: waipe-revisar-modelos
description: Revisão (semanal) do catálogo de modelos do framework a partir dos agentes publicados nos clientes, seguida de release do framework e atualização dos clientes. Use no template quando o usuário pedir "revisa os modelos", "atualiza o catálogo", "revisão semanal".
---

# Revisar os modelos do catálogo

Roda só no repositório template. Fonte: os agentes **publicados** (tags `<slug>/vX.Y.Z` em main) dos clientes.

## 1. Levantar o que é novo

1. Leia `.claude/waipe/catalogo/REVISOES.md` (data da última revisão e tags já vistas; crie se não existir).
2. `python3 .claude/waipe/waipe.py clientes` e, para cada repositório, `gh release list -R <repo>`: separe as tags
   publicadas depois da última revisão.
3. Baixe cada uma: `gh release download <tag> -R <repo> -D <pasta-temporária>/<repo>/<tag>`.

## 2. Comparar com o catálogo

Para cada agente novo ou alterado, classifique:

- **Modelo novo**: padrão que pode servir a outros clientes e não existe no catálogo.
- **Melhoria de modelo**: mesmo padrão de um modelo existente, com algo melhor (correção, node, layout, prompt).
- **Específico**: só faz sentido para aquele cliente. Não entra.

Apresente uma tabela (cliente, agente, versão, classificação, motivo) e pergunte ao usuário o que adotar.

## 3. Escrever os modelos adotados

Na `main` (branch única):

1. **Anonimize**: sem nome, CNPJ, e-mail, telefone, IDs de planilha/pasta/documento, URLs de cliente, nomes de
   pessoas ou vendedores; `credentialId: ""`; tokens como `SUBSTITUA_PELO_TOKEN`. Troque por valores de exemplo
   no `CONFIG` (`destinatarios: ["financeiro@exemplo.com"]`). O validador barra CNPJ e e-mail real.
   **ID de relatório do Data Lab** vira `SUBSTITUA_PELO_ID_DO_RELATORIO...`, mas o **texto (prompt) do relatório fica** no
   `.md`, na subseção "Relatórios do Data Lab (textos para criar)".
2. Generalize: o que varia de cliente para cliente vai para o `CONFIG` e vira pergunta.
3. Grave `.claude/waipe/catalogo/<slug>/<slug>.json` e `<slug>.md`. Os e-mails do modelo devem usar o **padrão de e-mail Waipe**
   (`.claude/waipe/modelos-comunicacao/kit-email-waipe.js`); se o agente do cliente usa outro desenho, adapte ao kit e
   descaracterize os dados do cliente. Crie também os **modelos de comunicação** dele em `.claude/waipe/catalogo/<slug>/modelos/`
   (peças e `modelos.json`, ver `.claude/waipe/modelos-comunicacao/PADRAO.md`), rodando os nodes do modelo com dados fictícios.
   O cabeçalho do `.md` traz `icone`, `resumo`, `frequencia` e `quem_recebe` (e `nota`, se houver), que o portal de modelos
   mostra no cartão. O `.md` segue o modelo de agente e tem também
   `## Quando usar` e `## Perguntas para personalizar` (as perguntas que a skill `waipe-criar-agente` fará).
   Melhoria de modelo existente: suba a `versao` e registre no Histórico.
4. Atualize a tabela de `INDICE.md` e registre a revisão em `REVISOES.md` (data, tags vistas, decisão de cada uma).
5. `python3 .claude/waipe/waipe.py validar` até passar.

## 4. Publicar e propagar

1. Escreva as mudanças em `## Não publicado` no `.claude/waipe/CHANGELOG.md`. Commit e
   `python3 .claude/waipe/waipe.py salvar`.
2. Com o ok do usuário: `python3 .claude/waipe/waipe.py release-framework minor` (patch se só ajustou modelos).
3. Ofereça atualizar os clientes (skill `waipe-atualizar-framework`, seção do template).
