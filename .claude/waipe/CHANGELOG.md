# Changelog do framework

Cada versão do `waipe-agentes-template`. Versão maior = o repositório do cliente precisa de alguma ação, descrita na seção.
A atualização nunca toca em `agentes/`, `CLAUDE.md`, `README.md` nem em `.claude/settings.local.json`.

## v3.0.0 (2026-10-22)
- **Ação no cliente (versão maior):** os modelos de comunicação saem de `agentes/modelos/` (galeria com `index.html`) e vão
  para dentro de cada agente, em `agentes/<slug>/modelos/`, só com as peças enviadas (e-mail como é enviado, conversa de
  WhatsApp, planilha, PDF) e a lista `modelos.json`. A moldura de apresentação e a galeria saem: quem mostra os modelos é o
  portal de modelos. Para migrar, siga o passo 6 da skill `waipe-atualizar-framework`.
- **Novo padrão de e-mail Waipe:** o kit `kit-email-waipe.js` passa ao desenho do consolidado do Guardião da Amostra Padrão
  (claro, com modo escuro automático, eyebrow dourado, indicadores em verde-oliva). Mesma API (`wpPagina`, `wpKpis`, ...);
  `wpPagina` agora devolve o documento completo e aceita `eyebrow` e `titulo`.
- Catálogo: os 6 modelos com os e-mails no padrão novo (o Coach dos Representantes passou a usar o kit) e versões novas;
  modelos de comunicação em `catalogo/<slug>/modelos/`, gerados rodando os nodes com dados fictícios. O cabeçalho dos `.md`
  ganha `icone`, `resumo`, `frequencia`, `quem_recebe` e `nota`, usados pelo portal.
- `modelos-comunicacao/rodar-node.mjs` e `comum.rodar_node`: rodam só o JavaScript de um node `code` com entradas fictícias
  (nada é enviado), para o modelo ser exatamente o que o node monta. `comum.py` passa a ter só as peças
  (`pagina_whatsapp`, `pagina_planilha`, `salvar_manifesto`); saem `kit_email.py`, `pagina_email`, `card` e `atualizar_indice`.
- `waipe.py`: `validar` confere `<agente>/modelos/modelos.json` (arquivos existentes, tipos, e-mails fictícios no catálogo);
  `status`, `catalogo` e `novo-agente` apontam para a pasta nova.

## v2.2.1 (2026-10-22)
- `modelos-comunicacao/comum.py`: a página de planilha aceitava no máximo 8 colunas (`IndexError` com 9 ou mais); agora aceita até 26.

## v2.2.0 (2026-10-22)
- **Modelos de comunicação dos agentes**: ao fechar a release de um agente que envia WhatsApp, e-mail, documento ou planilha, a IA cria os modelos navegáveis (WhatsApp interativo, e-mail, documento em PDF, consolidado do gestor e planilhas, com dados fictícios) em `agentes/modelos/<slug>/`. Se `agentes/modelos/` já existe, só acrescenta a pasta do agente e o cartão no `index.html`. Padrão e componentes em `.claude/waipe/modelos-comunicacao/` (`PADRAO.md`, `comum.py`, `exemplo_gerar.py`); skill `waipe-fechar-release`, regra do framework e README atualizados.
- `agentes/modelos/` é **pasta reservada**: `validar`, `status`, `novo-agente`, `release` e o hook não a tratam mais como agente (antes, `validar` falhava com "falta modelos.json"). `status` mostra `modelos: ok` ou `modelos: PENDENTE` para o agente que envia mensagens.
- **Padrão de teste:** o destino de teste fica direto no campo do node de envio (`phone`, `to`); nada de `modoTeste` no `CONFIG` nem prefixo "[TESTE]". Registrado na skill `waipe-flow`, na regra do framework e na skill `waipe-criar-agente`.

## v2.1.0 (2026-10-16)
- **Catálogo com os dois primeiros modelos** (v1.0.0 cada), anonimizados a partir de agentes em produção: `coach-dos-representantes` (com o flow auxiliar `adicionar-vendedores-em-metas`) e `guardiao-da-amostra-padrao`. Cada um traz quando usar, perguntas para personalizar, passo a passo de implantação em outro cliente, `CONFIG` e os textos dos relatórios do Data Lab. Seção "Modelos prontos" no `README.md`.
- **Padrão novo: salvar sempre o texto (prompt) de cada relatório do Data Lab** no `.md` do agente (subseção "Relatórios do Data Lab (textos para criar)" em "Configuração após importar"). No modelo de `.md`, na regra do framework, nas skills `waipe-criar-agente` e `waipe-revisar-modelos`. Em modelo de catálogo vai só o texto, nunca o ID. `validar` avisa quando o flow usa Data Lab e o `.md` não documenta o relatório.

## v2.0.1 (2026-10-09)
- `migrar` compara o conteúdo de `develop` e `main` (antes comparava commits e barrava repositórios em que o release antigo copiou os arquivos para a main).

## v2.0.0 (2026-10-09)
- **Branch única (`main`), sem `develop`, `feature/` nem PR.** Toda alteração vai para a `main` com `waipe.py salvar` (valida e envia) e o usuário testa a partir dela.
- **Release por agente, a pedido**: `waipe.py release <slug> <patch|minor|major|X.Y.Z>` troca `### v2.3.0 (2026-10-22)` do Histórico por `### vX.Y.Z (data)`, atualiza `versao`, cria a tag `<slug>/vX.Y.Z` e um GitHub Release com **todos os arquivos da pasta** do agente (inclui flows auxiliares). Skill `waipe-aprovar` virou `waipe-fechar-release`.
- Novos comandos `novo-agente <slug>` (substitui `feature`) e `migrar`. Saem `feature` e `entregar`. `atualizar` grava direto na `main`. `release-framework <nivel>` fecha o `## Não publicado` do CHANGELOG, sobe a `VERSION` e cria a tag.
- Agente novo nasce com `versao: 0.0.0` e `### Não publicado` no Histórico.
- **Ação no cliente (major):** depois de `atualizar`, rode `python3 .claude/waipe/waipe.py migrar` uma vez (apaga `develop` e deixa só a `main`).

## v1.3.0 (2026-10-09)
- `zapi_send` não serve para mídia em Base64 acima de ~190 KB (teto de 256 KB de expressão; um PDF real deu 612 KB e falhou com `ExpressionResultTooLarge`). Skill `waipe-flow` e guia (§4.21) mandam usar `http_request` na Z-API oficial (`send-document/pdf`, header `Client-Token`) nesses casos.

## v1.2.0 (2026-10-09)
- Z-API: a sandbox em `frontzap.com.br` (via `http_request`) vale só para os **testes iniciais**; em **produção** o padrão é o node `zapi_send` com a Z-API oficial. Skill `waipe-flow` e guia dos nodes (§4.11 e §4.21) corrigidos.

## v1.1.0 (2026-10-09)
- **Mudança sem JSON de flow vai direto para develop e main.** O `entregar` detecta quando a entrega não altera nenhum JSON de flow (agente ou modelo do catálogo) e, depois do merge em develop, publica em main: no cliente, só os commits da entrega (cherry-pick, sem arrastar agentes em teste); no template, develop inteiro, com tag e Release se a `VERSION` subiu. Regras de ferro 1, 2 e 5, `waipe-gitflow.md` e a skill `waipe-criar-agente` atualizadas. Mudança só no `.md` não sobe a versão do agente.
- **WhatsApp pela Z-API sandbox (`frontzap.com.br`).** Skill `waipe-flow` e guia dos nodes (§4.11 e §4.21) registram que os flows do projeto usam `http_request` para a instância sandbox, porque o `zapi_send` só envia para a Z-API oficial. Inclui o exemplo de envio de documento.
- `feature <assunto>` no template não cria mais pasta de agente.
- Inclui as correções da v1.0.1, que não chegou a ser publicada.

## v1.0.1 (2026-10-07)
- `novo-cliente` espera o GitHub terminar de copiar o template antes de clonar (antes clonava vazio) e copia a identidade de commit do template para o clone.
- `release <slug>` leva junto o `CLAUDE.md` e o `README.md` de develop (antes, mudança nas particularidades do cliente nunca chegava a main).
- `validar` avisa quando um node não tem conexão de entrada (nunca executa).

## v1.0.0 (2026-10-07)
- Primeira versão: estrutura de agentes (JSON + MD), validador, gitflow por agente (feature → develop → release → main com tag `<slug>/vX.Y.Z`), catálogo de modelos, skills de criação, aprovação, atualização e revisão de modelos.
