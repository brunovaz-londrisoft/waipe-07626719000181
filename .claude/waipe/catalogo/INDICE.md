# Catálogo de modelos

Modelos anônimos de agentes, usados pela skill `waipe-criar-agente` para sugerir um ponto de partida.
Cada modelo é uma pasta `<slug>/` com `<slug>.json` e `<slug>.md` (com as seções "Quando usar" e "Perguntas para personalizar").
Mantido pela skill `waipe-revisar-modelos`, rodada no repositório template.

Os **modelos de comunicação** de cada um (WhatsApp, e-mail, documento, consolidado e planilhas, com dados fictícios) ficam em `catalogo/<slug>/modelos/`, com a lista das peças em `modelos.json`. Todo e-mail dos modelos segue o **padrão de e-mail Waipe** (`.claude/waipe/modelos-comunicacao/kit-email-waipe.js`, desenho do Guardião da Amostra Padrão).

| Modelo | Gatilho | Para que serve | Palavras-chave |
|---|---|---|---|
| `anjo-do-primeiro-pedido` (v1.1.0) | agendado (toda terça, 07:00) | Radar dos clientes novos (1 compra só) que estão de 20 a 40 dias sem recomprar: lista por vendedor por WhatsApp e e-mail, planilha por vendedor e consolidado ao gestor. | cliente novo, primeira compra, recompra, vendedor, radar, pós-venda, WhatsApp |
| `clientes-inativos` (v1.1.0) | agendado (dia 1, 08:00) | E-mail de reativação a cada cliente parado (90 a 365 dias sem comprar), um por vez, e resumo dos notificados ao gestor. | clientes inativos, reativação, sem comprar, e-mail, resumo de envios |
| `coach-dos-representantes` (v1.1.0) | agendado (segunda e quinta, 07:00) | Resumo de performance por vendedor (vendas do mês x meta, carteira, pendências) com PDF por WhatsApp ou e-mail, e consolidado por e-mail ao gestor. Inclui o flow auxiliar `adicionar-vendedores-em-metas` (mantém a planilha de metas). | vendedores, representantes, metas, comissão, carteira, WhatsApp, PDF, resumo semanal |
| `giro-estoque` (v1.1.0) | agendado (segunda e quinta, 07:30) | Giro, cobertura e curva ABC por produto, planilha por fabricante e consolidado ao gestor com o ranking de ação imediata e a distribuição por status. | estoque, giro, cobertura, curva ABC, ruptura, compra, fabricante, estoque parado |
| `guardiao-da-amostra-padrao` (v1.2.0) | agendado (dias 4 e 15, 07:00) | Clientes que compraram em 12 meses e estão há mais de 40 dias sem comprar: uma planilha por vendedor no Google Sheets e e-mail consolidado ao gestor (ou aviso se não houver). | clientes adormecidos, inativos, reativação, última compra, planilha por vendedor |
| `pendencias-de-ontem` (v1.1.0) | agendado (todos os dias, 08:00) | E-mail da rotina da manhã com o que ficou pendente até ontem (orçamentos, vendas e O.S. não faturadas, contas vencidas) e o que vence hoje. | pendências, rotina da manhã, orçamentos, não faturadas, contas a pagar, contas a receber, vencidas |
