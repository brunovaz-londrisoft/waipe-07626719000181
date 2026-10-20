# Catálogo de modelos

Modelos anônimos de agentes, usados pela skill `waipe-criar-agente` para sugerir um ponto de partida.
Cada modelo é uma pasta `<slug>/` com `<slug>.json` e `<slug>.md` (com as seções "Quando usar" e "Perguntas para personalizar").
Mantido pela skill `waipe-revisar-modelos`, rodada no repositório template.

| Modelo | Gatilho | Para que serve | Palavras-chave |
|---|---|---|---|
| `coach-dos-representantes` (v1.0.0) | agendado (segunda e quinta, 07:00) | Resumo de performance por vendedor (vendas do mês x meta, carteira, pendências) com PDF por WhatsApp ou e-mail, e consolidado por e-mail ao gestor. Inclui o flow auxiliar `adicionar-vendedores-em-metas` (mantém a planilha de metas). | vendedores, representantes, metas, comissão, carteira, WhatsApp, PDF, resumo semanal |
| `guardiao-da-amostra-padrao` (v1.0.0) | agendado (dias 4 e 15, 07:00) | Clientes que compraram em 12 meses e estão há mais de 40 dias sem comprar: uma planilha por vendedor no Google Sheets e e-mail consolidado ao gestor (ou aviso se não houver). | clientes adormecidos, inativos, reativação, última compra, planilha por vendedor |
