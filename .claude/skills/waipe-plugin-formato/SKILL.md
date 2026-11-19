---
name: waipe-plugin-formato
description: Conhecimento do Waipe Páginas e do formato dos plugins (waipe-paginas/1): o que o motor faz, a linguagem de fórmulas, cada bloco do painel, as tabelas, as configurações e as regras de segurança. Carregue sempre antes de criar, alterar ou revisar um plugin.
---

# Waipe Páginas e o formato dos plugins

## A plataforma

O Waipe Páginas (repositório `waipe-paginas`, Next.js na Vercel, Neon Postgres) mostra páginas de indicadores e
relatórios sobre os dados do Waipe. **Um projeto Vercel e um banco por cliente.** Cada página é um plugin instalado em
**Configurações gerais > Páginas**, num **menu** escolhido na instalação (menus são cadastrados ali e a página pode
trocar de menu depois). **Instalar cria o schema da página no banco** (tabelas padrão + a tabela de itens com uma
coluna por campo da seção `banco`); **atualizar** (o `.json` de versão mais nova) mostra as versões e o que muda no
banco e aplica a migração.

Fluxo dos dados: relatório do **Data Lab** → Waipe Flow (agendado 07:00 ou botão "Atualizar agora") envia as linhas
em lotes → o **motor** (`waipe-paginas/src/lib/motor`) reconhece as colunas, calcula, grava a base e o histórico →
as telas leem a base. Toda página tem as abas Indicadores, Relatório, Consolidado (opcional), Atualizações e
Configurações (com a Integração: texto do Data Lab, ID do relatório, flows para baixar, webhook). Atualizações,
Integração e flows são da plataforma, iguais para todos.

Fontes de verdade (leia quando tiver dúvida, na cópia ao lado `../waipe-paginas`):
`docs/PLUGINS.md` (referência), `src/lib/motor/tipos.ts` (tipos exatos), `src/lib/motor/expr.ts` (fórmulas),
`src/lib/motor/painel.ts` (blocos), `src/lib/motor/validar.ts` (o que é recusado), `src/lib/motor/migracao.ts`
(o que a instalação e a atualização fazem no banco), `docs/BANCO.md`. Os plugins do catálogo
(`modelos/plugins/`) usam todos os recursos: copie deles.

## Fórmulas (sem eval: só calcula)

- Campos do item pelo nome (`estoque_atual`), parâmetros por `p.nome`, membros `p.grade[curva].critico`, `hoje`.
- `+ - * /` (divisão por 0 = nulo), `&` junta texto, `= <> < <= > >=`, `e ou nao`, `cond ? a : b`, `nulo verdadeiro falso`.
- Funções: `max min abs arred(x,c) teto piso numero texto vazio valor(a,b...)`, `dias(de,ate) data(x)`,
  `contem(nome,lista) casa(tipo,lista) igual(nome,lista) em(x,lista)`, `br(x,c) brl(x) pct(f) url(x) titulo(x)`,
  `rotulo('dominio',v) ordem('dominio',v)`.
- Agregadas (sobre um conjunto): `conta(cond) soma(x,cond) media mediana maior menor distintos primeiro`.
- Texto com `{{ fórmula }}`; marcações `**negrito**`, `[[destaque]]`, `` `código` ``. Nunca HTML.
- Cuidado: `nao a = b` é `(nao a) = b`; use parênteses. Nome de campo igual a função (ex.: `data`) funciona: `data(data)`.

## Estrutura do .json

1. Identidade: `formato`, `slug` (a-z 0-9 _, é a URL, o schema no banco e o nome do fluxo), `nome`, `rotulo`,
   `descricao`, `icone` (caixa, carteira, relogio, grafico, olho, tabela, fabrica, doc, grade, casa), `categoria {nome,
   icone}` (só o menu **sugerido** na instalação), `versao` (obrigatória; a release grava), `itens` (plural),
   `abas {relatorio, consolidado?}`.
2. `dataLab {relatorio, texto, colunas}`: o texto exato para criar o relatório. `integracao {agendamento {hora, minuto},
   passos [{titulo, blocos [{texto} | {ferramenta}]}]}`: os passos da aba Configurações > Integração (textos com
   `{{relatorio}}`, `{{nome}}`, `{{horario}}`); as ferramentas `datalab`, `id_relatorio`, `baixar_flows`, `webhook` e
   `testar` aparecem uma vez cada. Copie de um plugin existente e adapte os textos.
3. `parametros[]`: `{chave, tipo, rotulo, padrao, min, max, sufixo, ajuda}`; tipos `inteiro numero percentual
   (fração 0-1) texto lista booleano grade` (grade: `linhas`, `colunas [{chave, rotulo}]`, `crescente`).
   `validacoes [[fórmula do erro, mensagem]]`.
4. `colunas {campo: {rotulo, nomes[], obrigatoria, tipo texto/numero/data, max, trechos[], vazioParametro,
   semColuna, diferenteDe}}`. Nomes comparados sem acento, símbolo e caixa (`cliente_fornecedor` = `clientefornecedor`).
   Ponha nos `nomes` o que o Data Lab realmente devolve. `exigirUma [[a, b]]`.
5. `entrada {chave, campos [[campo, fórmula]], descartar[]}`: na carga (e refeitos ao recalcular).
6. `banco {tabela, campos {campo: tipo}, indices [[campos]], migracoes [{versao, passos}]}`: a tabela da página.
   Tipos `texto numero inteiro data booleano`; nomes em minúsculas (a-z, 0-9, _), sem `empresa chave ativo criado_em
   atualizado_em alterado_em ultima_carga`. **Toda coluna do Data Lab, todo campo de entrada e tudo o que as telas
   leem** (relatório, consolidado, detalhe, histórico, painel) precisa estar em `campos`; o resto do cálculo é
   temporário e não fica no banco. Data vai como "aaaa-mm-dd" (vazia = nulo).
   **Atualização:** campo novo vira coluna sozinho. Renomear, apagar ou mudar tipo de campo que já existe exige passo
   explícito na versão nova: `{"renomear": {"de", "para"}}`, `{"remover": "campo"}`, `{"mudarTipo": {"campo", "tipo"}}`
   (a tela pede confirmação, e é release **major**). Tipo diferente sem passo bloqueia a atualização.
7. `calculo[]` em ordem: `{campo, formula}`, `{campo, casos [[cond, valor]], senao}`, `{descartar}`,
   `{pareto {campo, valor, desempate, cortes [[fórmula do corte, nome]], resto}}`.
8. `dominios {campo: {estilo? selo|curva, valores {v: {rotulo, curto, icone, cor, ordem}}}}`: rótulos, cores e ordem.
9. `resumo {nome: fórmula agregada | {contarPor: campo} | {somarPor: campo, valor}}`: KPIs e evolução diária saem daqui.
10. `grupos {nome: {campo, por, filtro, metricas {m: agregada}, ordem [[fórmula, asc|desc]]}}`.
11. `historico {descricao, campos [{campo, titulo, numero?, dominio?}]}`: o que conta como mudança (não use campos
    que mudam todo dia, como dias em aberto).
12. `painel {titulo, texto, exportar {excel, imprimir, arquivo, abaIndicadores}, kpis[], blocos[]}`. KPI: `{chave, rotulo, valor (fórmula sobre o resumo), nota,
    unidade, link, menorMelhor, forte}`. Blocos (todos com `largura` 4/6/8/12, `titulo`, `sub`, `nota`, `excel` = aba no Excel, `excelColunas` = títulos dela):
    - `distribuicao {campo, dominio, estilo lista|legenda, barra, extra (agregada), extraTitulo, detalhe, link}`
      (detalhe usa `qtd pct extra`; link usa `valor`)
    - `matriz {linhas {campo, dominio}, colunas {campo, dominio}, link (linha, coluna)}`
    - `participacao {campo, dominio, soma, acao, acaoTitulo, rotulos [2], link}` (curva ABC)
    - `evolucao {series [{chave, rotulo, cor, valor (sobre o resumo)}]}`
    - `tabela {fonte? (grupo), filtro, ordem, limite, classe, colunas [{titulo, valor (texto), numero, negrito,
      dominio, campo, link, sub}], mais {link, texto, sempre}, vazio}` (texto usa `total` = linhas filtradas)
    - `faixas {valor, filtro, faixas [[rótulo, de, até|null]], medida (agregada), formato, dica, ocultarVazias, cor, link (de, ate)}`
    - `ranking {por, dominio, filtro, a, b, total (agregadas), manter, ordem, limite, cores, legendas, valor, link (nome, valor)}`
    - `ultima` (última atualização) e `nota`.
13. `relatorio {titulo, texto, tabela {titulo, arquivo, colunas[], busca[], ordem {campo, desc}, periodo
    [{campo, titulo}] (filtro 📅), cartoes [{rotulo, valor, nota, forte}], distribuicao {campo, dominio},
    abaResumo {nome, campo, dominio, colunas}, exportar {excel, csv, imprimir, colunas}, vazio}}`. Coluna: `{campo, titulo, tipo, dominio, casas, filtro
    multi|faixa|texto, destaque, largura, larguraExcel, vazio, data, link}`. Filtro em destaque segue a ordem das colunas.
14. `consolidado {titulo, texto, grupo, tabela {..., posicao}}` e `detalhe {titulo, sub, voltar {texto, link},
    selo {campo, dominio}, fatos [[rótulo, valor]]}` (o item tem `ativo`).
15. `configuracao {titulo, ajuda, explicacao {titulo, passos, exemplo {titulo, maior, filtro, linhas}}, secoes
    [{titulo, sub, itens}], previa {campo, dominio, rotulo, outros, extra}, fora[]}`. Itens: `parametros {chaves}`,
    `trava {chave, aviso, passos, confirmar}`, `cortes {chaves, rotulos}`, `grade {chave, dominio, cores}`,
    `regras {itens [{dominio, valor, texto}]}`, `tabela {cabecalho, linhas}`, `texto`, `listas {cabecalho, chaves}`, `colunas`.

## Segurança e o que a validação recusa

Links só internos (começam com `/`), cores `#rrggbb` ou `var(--nome)`, fórmula que não compila, função fora da
lista, parâmetro inexistente citado na configuração, domínio ou grupo inexistente, slug reservado. Até 512 KB.
O plugin é instalado por usuário da empresa: nunca coloque dado real, ID de relatório, token ou URL de cliente.
