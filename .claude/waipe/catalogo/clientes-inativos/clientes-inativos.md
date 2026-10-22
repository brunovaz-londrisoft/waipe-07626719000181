---
nome: Agente de Clientes Inativos
slug: clientes-inativos
versao: 1.1.0
modelo_base: nenhum
gatilho: agendado (dia 1 de cada mês, 08:00, America/Sao_Paulo)
icone: 💤
resumo: Reativa clientes de 90 a 365 dias sem comprar com um e-mail e manda o resumo dos notificados ao gestor.
frequencia: Dia 1 de cada mês, 08:00
quem_recebe: Cada cliente inativo e o gestor
atualizado: 2026-10-22
---

# Agente de Clientes Inativos

## Quando usar

Cliente que quer **reativar clientes parados**: quem comprou pela última vez entre X e Y dias atrás (padrão: entre 90 e 365)
recebe um e-mail de reativação, um por vez, e o gestor recebe um resumo dos clientes notificados.

Palavras-chave: clientes inativos, reativação, sem comprar, e-mail em massa, resumo de envios, carteira.

Modelos de comunicação (e-mail ao cliente e resumo do gestor): `.claude/waipe/catalogo/clientes-inativos/modelos/` (lista das peças em `modelos.json`).

## Perguntas para personalizar

1. **Nome da empresa**, **assinatura** e **telefones** (fixo e WhatsApp) que vão no e-mail ao cliente.
2. **Janela de inatividade** (padrão: mais de 90 e menos de 365 dias).
3. **Texto do e-mail**: chamada, parágrafos e assunto. O cliente tem um texto aprovado?
4. **Quando rodar** (padrão: dia 1 de cada mês, 08:00).
5. **E-mail do gestor** que recebe o resumo e o nome dele.
6. **DDD padrão** para celular que vem sem DDD e nomes a ignorar (além do CONSUMIDOR FINAL).
7. O relatório de clientes traz **e-mail e data da última compra**?

## Objetivo

Reativar clientes que pararam de comprar: busca a carteira no Data Lab, separa quem fez a última compra dentro da janela
e manda um e-mail de reativação a cada um (um por vez, com pausa de 1 segundo). Ao concluir, manda ao gestor um resumo com
os clientes notificados e a data da última compra de cada um.

## Como funciona

| # | Node | Tipo | O que faz |
|---|---|---|---|
| 1 | Agendamento | trigger_schedule | Mensal, no dia 1, às 08:00 (`America/Sao_Paulo`). |
| 2 | Waipe Data | waipe_data | Relatório do Data Lab com os clientes, a última compra e os contatos. |
| 3 | Filtrar Inativos 90 a 365 dias | code | Junta os registros de todas as empresas, aplica a janela, ignora CONSUMIDOR FINAL, valida e-mail e celular, tira contatos repetidos e monta o e-mail de cada cliente (padrão de e-mail Waipe). |
| 4 | Um E-mail por Vez | loop | Percorre `clientes_email` em lotes de 1, com pausa de 1 s. A saída `loop` envia; `done` segue para o resumo. |
| 5 | Enviar E-mail de Reativação | gmail_send | Envia o e-mail ao cliente (continua em caso de erro). |
| 6 | Montar Resumo | code | Ao concluir o loop, monta o resumo: total notificado, falhas e a tabela de clientes. |
| 7 | Enviar Resumo | gmail_send | Envia o resumo ao gestor. |

Campos que o node 3 entrega por cliente: `codigo`, `nome`, `nome_saudacao`, `dtultimacompra`, `dias_sem_comprar`, `email`,
`tem_email`, `celular_whatsapp`, `tem_celular`, `email_assunto`, `email_html`, `whatsapp_texto`. O ramo de WhatsApp não existe
no flow: o node 3 ainda monta `whatsapp_texto` e `celular_whatsapp`, sem uso, para quem quiser acrescentar o envio depois.

Falha de envio do Gmail não aparece no resumo (o node continua em caso de erro): a lista mostra os clientes que entraram no loop.

## Como implantar em um cliente novo

1. Peça "quero criar o agente de clientes inativos": a skill `waipe-criar-agente` copia este modelo e faz as perguntas acima.
2. Crie o relatório do Data Lab com o texto abaixo e cole o ID no node Waipe Data.
3. Importe o JSON, conecte a conta Google nos dois nodes de Gmail e ajuste o `CONFIG` do node 3 (nome, assinatura, telefones, textos).
4. Teste com o destino do node 5 trocado por um e-mail interno, volte para `{{ $json.email }}` e ative.

## Configuração após importar

- **Gmail** (nodes 5 e 7): selecionar a conta Google conectada.
- **Relatório do Data Lab**: trocar `SUBSTITUA_PELO_ID_DO_RELATORIO` pelo ID do relatório criado.
- **Destinatário do resumo** (node 7): trocar `gestor@exemplo.com`.

### Relatório do Data Lab (texto para criar)

| Node | Texto do relatório |
|---|---|
| Waipe Data | `Liste todos clientes com código, nome, e-mail, telefone, celular e data da ultima compra.` |

`CONFIG` do node **Filtrar Inativos 90 a 365 dias**:

| Constante | Valor no modelo | Para que serve |
|---|---|---|
| `DIAS_MIN` / `DIAS_MAX` | 90 / 365 | Janela de inatividade (exclusiva nas duas pontas). |
| `NOME_REMETENTE`, `NOME_LOJA`, `TELEFONE_LOJA` | "", "NOME DA EMPRESA", "" | Assinatura; linha vazia é omitida. |
| `ASSUNTO_EMAIL` | "Olá, aqui é da NOME DA EMPRESA" | Assunto do e-mail. |
| `CHAMADA_EMAIL` | "Sentimos sua falta! Podemos ajudar?" | Frase em destaque no topo do e-mail. |
| `ASSINATURA_EMAIL` | "NOME DA EMPRESA \| Soluções e Acabamentos" | Assinatura do e-mail. |
| `TELEFONE_FIXO_EMAIL` / `TELEFONE_WHATSAPP_EMAIL` | (00) 0000-0000 / (00) 00000-0000 | Telefones da assinatura. |
| `DDD_PADRAO` | "11" | DDD para celular que vem sem DDD. |
| `USAR_FONE_SE_FOR_CELULAR` | false | Usa o campo `fone` quando `celular` está vazio. |
| `IGNORAR_NOMES` | CONSUMIDOR FINAL | Nomes que nunca recebem mensagem. |

O texto dos parágrafos do e-mail está nas constantes `PARAGRAFOS_EMAIL` do mesmo node. `CONFIG` do node **Montar Resumo**: `TITULO`,
`EMPRESA`, `ROTULO_RELATORIO`, `NOME_GESTOR` e `LIMITE_LINHAS`.

## Como testar

1. Importe `clientes-inativos.json` no Waipe Flow e conecte o Gmail.
2. Troque o `to` do node 5 por um e-mail de teste e rode: o cliente da janela com e-mail recebe o e-mail (1 por segundo) e, ao fim, chega o resumo.
3. Volte o `to` para `{{ $json.email }}` e ative o agendamento.

## Histórico

### v1.1.0 (2026-10-22)
- E-mails no novo padrão de e-mail Waipe (claro, com modo escuro automático, desenho do Guardião da Amostra Padrão), com o kit `kit-email-waipe.js`. Modelos de comunicação em `modelos/`, dentro da pasta do modelo, só com as peças enviadas, gerados rodando os nodes com dados fictícios.

### v1.0.0 (2026-10-22)
- Primeira versão do modelo no catálogo, anonimizada a partir de um agente em produção em um cliente, com os e-mails no padrão Waipe.
