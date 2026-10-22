---
name: waipe-criar-agente
description: Cria um agente novo (flow do Waipe Flow) ou altera um existente neste repositório, do pedido até o envio para a main, onde o usuário testa. Use quando o usuário disser "quero criar um agente", "novo agente de X", "altera o agente Y", "o agente Z falhou no teste" ou pedir um flow novo.
---

# Criar ou alterar um agente

Resultado: `agentes/<slug>/<slug>.json` + `agentes/<slug>/<slug>.md`, validados e enviados para a `main` (branch única) para o usuário testar.
Ferramenta: `python3 .claude/waipe/waipe.py` (abaixo, só `waipe`).

## 1. Entender e buscar parecidos

1. Resuma o pedido numa frase e confirme se é agente **novo** ou **alteração** (veja `waipe status`).
2. **Consulte sempre o catálogo antes de desenhar qualquer coisa**: rode `waipe catalogo <palavras do pedido>` (ex.:
   `waipe catalogo vendedor radar whatsapp`; sem palavras, lista tudo) e leia o `.md` dos modelos que combinam (gatilho,
   fonte de dados, saída, palavras-chave). Olhe também `agentes/` do cliente: um agente parecido daqui pode servir de base.
   Cada modelo tem os **modelos de comunicação** (WhatsApp, e-mail, documento, consolidado, planilhas) em
   `.claude/waipe/catalogo/<modelo>/modelos/` (lista em `modelos.json`): abra as peças para mostrar ao usuário como fica.
3. **Sugira o modelo mais parecido ao usuário** (até 3 candidatos: o que cada um faz e o que teria que mudar) e deixe
   **ele decidir**: usar um modelo como base ou criar do zero (AskUserQuestion). Não escolha sozinho. Se nenhum
   combina, diga que não há modelo parecido e siga do zero.
4. Se o usuário aceitar um modelo, crie o agente a partir dele: `waipe novo-agente <slug> --modelo <modelo>`. O comando
   copia o `.json` e o `.md` (e os flows auxiliares) para `agentes/<slug>/` com `versao: 0.0.0` e `modelo_base` preenchido; daí
   em diante é personalizar (passos 2 a 5).

## 2. Perguntar só o necessário

Use AskUserQuestion, no máximo 4 perguntas por rodada, com opções concretas. Comece pelas "Perguntas para
personalizar" do modelo escolhido e complete com o que faltar entre:

- **Gatilho**: manual, agendado (dias, horário, fuso), webhook ou WhatsApp (Z-API).
- **Dados**: Waipe Data / Data Lab (qual relatório ou prompt), API externa, planilha.
- **Regra de negócio**: filtros, cortes (dias, valores), o que é anomalia, o que excluir (ex.: CONSUMIDOR FINAL).
- **Saída**: e-mail (para quem, assunto), planilha, WhatsApp, resposta de webhook; com IA ou não.
- **Silêncio**: o que fazer quando não há nada a reportar.

Não pergunte o que o modelo, o `CLAUDE.md` do cliente ou um padrão do guia já respondem: proponha e deixe o
usuário corrigir.

## 3. Aprovar o desenho

Mostre o desenho antes de gerar: tabela dos nodes (nome, tipo, o que faz), `CONFIG` previsto e credenciais.
Para alteração, mostre o que muda e a nova versão (patch, minor ou major, ver regras). Espere o ok.

## 4. Gerar

1. Agente novo: `waipe novo-agente <slug>` (slug curto em kebab-case, ex.: `clientes-inativos`), ou
   `waipe novo-agente <slug> --modelo <modelo>` se o usuário aceitou um modelo do catálogo. Cria a pasta e o `.md`. Alteração: trabalhe direto nos arquivos existentes. Sempre na `main`.
2. Carregue a skill `waipe-flow` e gere o JSON completo em `agentes/<slug>/<slug>.json`. Flow grande: pode delegar
   ao subagente `waipe-flow` passando o desenho aprovado.
3. Preencha o `.md`: cabeçalho (`nome`, `modelo_base` = slug do modelo ou `nenhum`, `gatilho`), Objetivo, Como
   funciona, Configuração após importar e Como testar. No Histórico, uma linha por mudança em `### Não publicado`
   (no topo). **Não mexa em `versao`**: ela só muda quando a release é fechada.
   Se o flow usa Data Lab (`waipe_data` com `data_lab`), registre o **texto (prompt) de cada relatório** na subseção
   "Relatórios do Data Lab (textos para criar)" e atualize-a sempre que o relatório mudar.
   Se o agente envia WhatsApp ou e-mail a terceiros, gere com o **destino de teste direto no campo do node de envio**
   (sem `modoTeste` no `CONFIG`) e documente a troca para produção numa tabela "Destinos".
4. `waipe validar agentes/<slug>` até passar (o hook já valida a cada edição).

## 5. Enviar para teste

1. `git add agentes/<slug>` e commit `feat(<slug>): ...` (ou `fix(<slug>): ...`, `docs(<slug>): ...`).
2. `waipe salvar` (valida e envia para a `main`).
3. Diga ao usuário: importar `agentes/<slug>/<slug>.json` da `main` no Waipe Flow, o que conectar e o que conferir
   (seção "Como testar"). Quando ele achar bom e pedir, a skill `waipe-fechar-release` fecha a versão.

Se o modelo do catálogo precisou de muita adaptação ou faltou um modelo, anote isso no fim da resposta: é insumo
para a próxima revisão de modelos.
