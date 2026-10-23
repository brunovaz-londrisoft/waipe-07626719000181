# Revisões do catálogo

Registro da skill `waipe-revisar-modelos`: quando rodou, quais tags de clientes foram vistas e o que se decidiu.
A próxima revisão considera só tags publicadas depois da última data abaixo.

| Data | Cliente | Tag | Decisão |
|---|---|---|---|
| 2026-10-16 | cliente piloto (anônimo) | `coach-dos-representantes/v5.0.0` | Adotado como modelo 1.0.0 (inclui o flow auxiliar `adicionar-vendedores-em-metas`). Anonimizado: IDs do Data Lab, planilha, e-mails, nomes e contatos viraram placeholders; prompts dos relatórios documentados. |
| 2026-10-16 | cliente piloto (anônimo) | `guardiao-da-amostra-padrao/v1.0.0` | Adotado como modelo 1.0.0. Anonimizado do mesmo jeito; prompt do relatório documentado. |
| 2026-10-22 | clientes piloto (anônimos) | `anjo-do-primeiro-pedido/v1.0.0` | Adotado como modelo 1.0.0, anonimizado; e-mails no padrão Waipe. |
| 2026-10-22 | clientes piloto (anônimos) | `clientes-inativos/v3.0.0` | Adotado como modelo 1.0.0, anonimizado; e-mails no padrão Waipe (o e-mail ao cliente deixa de ser texto simples). |
| 2026-10-22 | clientes piloto (anônimos) | `giro-estoque/v2.0.1` | Adotado como modelo 1.0.0, anonimizado; e-mail no padrão Waipe. |
| 2026-10-22 | clientes piloto (anônimos) | `pendencias-de-ontem/v1.0.0` | Adotado como modelo 1.0.0, anonimizado; e-mail no padrão Waipe (sem logotipo em imagem). |
| 2026-10-23 | cliente piloto (anônimo, repositório compartilhado) | `comissao-mensal-gerencia-vendedores` v1.0.0 | Adotado como modelo 1.0.0 (novo: fluxo 41% igual ao mais parecido). Descaracterizado; problemas do flow de origem corrigidos (loop sem entrada, `RAW`, filtro do último dia solto); e-mails no padrão Waipe num node "Montar E-mail" para a gerência e para o vendedor. |
| 2026-10-23 | cliente piloto (anônimo, repositório compartilhado) | `guardiao-da-carteira` v1.0.0 | Adotado como modelo 1.0.0 (novo: fluxo 37% igual ao mais parecido; não é o Guardião da Amostra Padrão). Descaracterizado (destino, ID do Data Lab, chave do Ploomes); e-mail no padrão Waipe em "Montar E-mail do Relatório". |
| 2026-10-23 | cliente piloto (anônimo, repositório compartilhado) | `cmv-mensal` v1.0.0 | Adotado como modelo 1.0.0 (novo: fluxo 28% igual ao mais parecido). Descaracterizado (destinos, ID do Data Lab, códigos ignorados); gatilho manual trocado pelo webhook "Receber período" que o cálculo esperava; e-mail no padrão Waipe em "Montar E-mail do CMV"; planilha `anyone_reader`. |
| 2026-10-23 | cliente piloto (anônimo, repositório compartilhado) | `produtos-sem-giro` v1.0.0 | Adotado como modelo 1.0.0 (novo: fluxo 36% igual ao mais parecido). Descaracterizado (destinos, IDs do Data Lab, códigos ignorados); 3 e-mails no padrão Waipe em nodes "Montar E-mail ..."; travessão do título trocado; planilha `anyone_reader`. |
| 2026-10-23 | todos os repositórios da conta | (comparação) | Primeira rodada de `comparar-catalogo`: os outros 6 agentes publicados já estão no catálogo com o mesmo fluxo. |
| 2026-10-22 | (todos os modelos) | framework v3 | E-mails no novo padrão Waipe (desenho do Guardião, claro com modo escuro); Coach passou a usar o kit. Modelos de comunicação em `<slug>/modelos/`, gerados rodando os nodes com dados fictícios. Versões: Anjo 1.1.0, Inativos 1.1.0, Coach 1.1.0, Giro 1.1.0, Guardião 1.2.0, Pendências 1.1.0. |
| 2026-10-22 | clientes piloto (anônimos) | `guardiao-da-amostra-padrao`, `coach-dos-representantes` | Melhoria dos modelos existentes: e-mails no padrão Waipe (Guardião 1.1.0) e e-mail do vendedor responsivo (Coach 1.0.1). |
