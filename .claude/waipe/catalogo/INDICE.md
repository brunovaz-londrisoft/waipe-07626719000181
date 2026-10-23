# Catálogo de modelos

Modelos anônimos de agentes, usados pela skill `waipe-criar-agente` para sugerir um ponto de partida.
Cada modelo é uma pasta `<slug>/` com `<slug>.json` e `<slug>.md` (com as seções "Quando usar" e "Perguntas para personalizar").
Mantido pela skill `waipe-revisar-modelos`, rodada no repositório template.

Os **modelos de comunicação** de cada um (WhatsApp, e-mail, documento, consolidado e planilhas, com dados fictícios) ficam em `catalogo/<slug>/modelos/`, com a lista das peças em `modelos.json`. Todo e-mail dos modelos segue o **padrão de e-mail Waipe** (`.claude/waipe/modelos-comunicacao/kit-email-waipe.js`, desenho do Guardião da Amostra Padrão).

| Modelo | Gatilho | Para que serve | Palavras-chave |
|---|---|---|---|
| `anjo-do-primeiro-pedido` (v1.1.0) | agendado (toda terça, 07:00) | Radar dos clientes novos (1 compra só) que estão de 20 a 40 dias sem recomprar: lista por vendedor por WhatsApp e e-mail, planilha por vendedor e consolidado ao gestor. | cliente novo, primeira compra, recompra, vendedor, radar, pós-venda, WhatsApp |
| `clientes-inativos` (v1.1.0) | agendado (dia 1, 08:00) | E-mail de reativação a cada cliente parado (90 a 365 dias sem comprar), um por vez, e resumo dos notificados ao gestor. | clientes inativos, reativação, sem comprar, e-mail, resumo de envios |
| `cmv-mensal` (v1.0.0) | webhook (POST com o período; sem período, mês anterior) | CMV, vendas, lucro bruto e margem do período por mês, empresa e produto, com planilha nova, e-mail de resumo e resposta em JSON. | CMV, custo da mercadoria vendida, margem, lucro bruto, fechamento do mês, compras, webhook |
| `coach-dos-representantes` (v1.1.0) | agendado (segunda e quinta, 07:00) | Resumo de performance por vendedor (vendas do mês x meta, carteira, pendências) com PDF por WhatsApp ou e-mail, e consolidado por e-mail ao gestor. Inclui o flow auxiliar `adicionar-vendedores-em-metas` (mantém a planilha de metas). | vendedores, representantes, metas, comissão, carteira, WhatsApp, PDF, resumo semanal |
| `comissao-mensal-gerencia-vendedores` (v1.0.0) | agendado (último dia do mês, 23:30) | Fechamento mensal de comissões por venda faturada (tabela de faixas por desconto): ranking por vendedor e planilha geral à gerência, e-mail com planilha individual a cada vendedor. | comissão, vendedores, fechamento do mês, nota fiscal, desconto, faixas, ranking, planilha |
| `giro-estoque` (v1.1.0) | agendado (segunda e quinta, 07:30) | Giro, cobertura e curva ABC por produto, planilha por fabricante e consolidado ao gestor com o ranking de ação imediata e a distribuição por status. | estoque, giro, cobertura, curva ABC, ruptura, compra, fabricante, estoque parado |
| `guardiao-da-amostra-padrao` (v1.2.0) | agendado (dias 4 e 15, 07:00) | Clientes que compraram em 12 meses e estão há mais de 40 dias sem comprar: uma planilha por vendedor no Google Sheets e e-mail consolidado ao gestor (ou aviso se não houver). | clientes adormecidos, inativos, reativação, última compra, planilha por vendedor |
| `guardiao-da-carteira` (v1.0.0) | agendado (toda sexta, 17:00) | Cruza a última compra no Gestor com as interações do Ploomes e classifica cada cliente por cor (verde a vermelho), com planilha nova e e-mail ao gestor com a distribuição por status. | carteira, Ploomes, CRM, última compra, último contato, status, semáforo |
| `pendencias-de-ontem` (v1.1.0) | agendado (todos os dias, 08:00) | E-mail da rotina da manhã com o que ficou pendente até ontem (orçamentos, vendas e O.S. não faturadas, contas vencidas) e o que vence hoje. | pendências, rotina da manhã, orçamentos, não faturadas, contas a pagar, contas a receber, vencidas |
| `produtos-sem-giro` (v1.0.0) | agendado (dias úteis, 07:00) | Produtos com 20 dias ou mais sem venda (valor empatado, planilha e alerta) e ranking dos mais vendidos com cobertura de estoque e selo de reposição, por e-mail a compras. | estoque parado, sem giro, sem venda, mais vendidos, cobertura, reposição, compras |
