// Prévia de um plugin do Waipe Páginas para o simulador do portal de modelos (portal-modelos-waipe).
// Uso: node .claude/waipe/plugin/previa.mjs <pasta-do-plugin> [...]   (chamado por plugins.py gerar-modelos)
// Roda o motor do waipe-paginas (variável WAIPE_PAGINAS ou a pasta irmã ../waipe-paginas) com o exemplo.json
// (dados fictícios) e grava em <pasta>/modelos/ a simulação completa da página:
//   fluxo.json         o flow agendado que a página gera (Configurações > Integração), o mesmo que vai para o cliente
//   datalab.html       o relatório do Data Lab (texto para criar + linhas de exemplo)   → node "Waipe Data"
//   painel.html        aba Indicadores                                                   → node "Finalizar Carga no Painel"
//   relatorio.html     aba Relatório;  consolidado.html (se houver);  configuracoes.html (parâmetros e integração)
//   modelos.json       peças (com o node do flow que mostra cada uma) e o fluxo, lidos pelo simulador do portal.
// O HTML usa o CSS da própria plataforma, então o desenho é o mesmo da tela.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const raiz = resolve(import.meta.dirname, "../../..");
const paginas = resolve(process.env.WAIPE_PAGINAS || join(raiz, "..", "waipe-paginas"));
const motorDir = join(paginas, "src/lib/motor");
if (!existsSync(join(motorDir, "motor.ts"))) {
  console.error(`Motor não encontrado em ${motorDir}. Clone o waipe-paginas ao lado deste repositório ou defina WAIPE_PAGINAS.`);
  process.exit(3);
}
const imp = (f) => import(pathToFileURL(join(motorDir, f)).href);
const { validarPlugin } = await imp("validar.ts");
const { calcular, padrao, preparar, resumir } = await imp("motor.ts");
const { montarPainel } = await imp("painel.ts");
const { texto: textoExpr } = await imp("expr.ts");
const { agrupar } = await imp("motor.ts");
const { montarFlow } = await imp("flows.ts");
const { passosProntos, horario } = await imp("integracao.ts");
const css = readFileSync(join(paginas, "src/app/globals.css"), "utf8");
const plataforma = JSON.parse(readFileSync(join(paginas, "package.json"), "utf8")).version;

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const num = (n, c = 0) => Number(n || 0).toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c });
const dataBR = (d) => (/^\d{4}-\d{2}-\d{2}/.test(String(d ?? "")) ? `${String(d).slice(8, 10)}/${String(d).slice(5, 7)}/${String(d).slice(0, 4)}` : "");
// Links da prévia não levam a lugar nenhum: o conteúdo aparece sem o link.
const talvez = (classe, conteudo, estilo = "", dica = "") =>
  `<span${classe ? ` class="${classe}"` : ""}${estilo ? ` style="${estilo}"` : ""}${dica ? ` title="${esc(dica)}"` : ""}>${conteudo}</span>`;

function pagina(titulo, corpo) {
  return `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(titulo)}</title>
<style>${css}
:root { --fonte: Inter, system-ui, sans-serif; }
body { background: var(--bg); margin: 0; }
.previa { max-width: 1280px; margin: 0 auto; padding: 20px 16px 40px; }
.previa-aviso { font-size: 12px; color: var(--mut); margin: 0 0 14px; }
.previa h1 { font-size: 20px; margin: 0 0 4px; color: var(--tx); }
.previa .sub { color: var(--tx2); font-size: 13px; margin: 0 0 16px; }
</style></head>
<body><main class="previa">${corpo}</main></body></html>
`;
}

// ------------------------------------------------------------------ painel (mesmo desenho de Blocos.tsx)

function kpi(k) {
  const delta = k.anterior === null ? null : k.valor - k.anterior;
  const bom = delta === null || delta === 0 ? null : (delta < 0) === k.menorMelhor;
  const pe = delta !== null
    ? `<span class="delta${bom === null ? "" : bom ? " bom" : " ruim"}">${delta === 0 ? "= igual ontem" : `${delta > 0 ? "▲" : "▼"} ${num(Math.abs(delta))} vs. ontem`}</span>`
    : `<span class="delta">${esc(k.nota)}</span>`;
  return `<div class="kpi-p${k.forte ? " forte" : ""}"><small>${esc(k.rotulo)}</small><b>${num(k.valor)}${k.unidade ? `<em> ${esc(k.unidade)}</em>` : ""}</b><div class="kpi-pe">${pe}</div>${delta !== null && k.nota ? `<span class="kpi-nota">${esc(k.nota)}</span>` : ""}</div>`;
}

function celula(c) {
  let x = c.negrito ? `<b>${esc(c.texto)}</b>` : esc(c.texto);
  if (c.selo) x = `<span class="selo st-${esc(c.selo)}">${esc(c.texto)}</span>`;
  if (c.curva) x = `<span class="curva curva-${esc(c.curva.toLowerCase())}">${esc(c.texto)}</span>`;
  return `<td${c.numero ? ' class="num"' : ""}>${x}${c.sub ? `<small class="sub">${esc(c.sub)}</small>` : ""}</td>`;
}

function conteudo(b) {
  switch (b.tipo) {
    case "distribuicao": {
      const barra = b.barra ? `<div class="saude-barra">${b.itens.filter((i) => i.qtd > 0).map((i) => talvez("", "", `flex-grow:${i.qtd};background:${i.cor}`, `${i.rotulo}: ${num(i.qtd)}`)).join("")}</div>` : "";
      const lista = b.estilo === "lista"
        ? `<div class="saude-lista">${b.itens.map((i) => talvez("saude-item", `<i style="background:${i.cor}"></i><span class="saude-rot">${esc(i.rotulo)}</span><b>${num(i.qtd)}</b><small>${esc(i.detalhe)}</small>`)).join("")}</div>`
        : `<ul class="dist-legenda">${b.itens.map((i) => `<li><span><i style="background:${i.cor}"></i>${esc(i.icone)} ${esc(i.rotulo)} <b>${num(i.qtd)}</b>${esc(i.detalhe)}</span></li>`).join("")}</ul>`;
      return barra + lista;
    }
    case "matriz":
      return `<div class="matriz-rolagem"><table class="matriz"><thead><tr><th></th>${b.colunas.map((c) => `<th><span class="matriz-ic">${esc(c.icone)}</span>${esc(c.rotulo)}</th>`).join("")}<th>Total</th></tr></thead><tbody>${b.linhas.map((l, li) => `<tr><th>${l.estilo === "curva" ? `<span class="curva curva-${esc(l.valor.toLowerCase())}">${esc(l.valor)}</span>` : esc(l.rotulo)}</th>${b.celulas[li].map((c) => {
        const forte = Math.round((c.qtd / b.max) * 70);
        return `<td${c.qtd ? ` style="background:color-mix(in srgb, var(--azul) ${forte}%, var(--card))"` : ""}${forte > 40 ? ' class="escuro"' : ""}>${c.qtd ? num(c.qtd) : '<span class="zero">0</span>'}</td>`;
      }).join("")}<td class="tot">${num(b.celulas[li].reduce((a, c) => a + c.qtd, 0))}</td></tr>`).join("")}</tbody></table></div>`;
    case "participacao":
      return `<div class="abc">${b.itens.map((c) => talvez("abc-linha", `<span class="curva curva-${esc(c.valor.toLowerCase())}">${esc(c.valor)}</span><div class="abc-barras"><div><span class="abc-trilho"><span style="width:${c.pctItens}%"></span></span><small>${esc(c.rotulos[0])}</small></div><div><span class="abc-trilho forte"><span style="width:${c.pctSoma}%"></span></span><small>${esc(c.rotulos[1])}</small></div></div><span class="abc-acao">${num(c.acao)}<small>ação</small></span>`)).join("")}</div>`;
    case "tabela":
      if (!b.linhas.length) return `<p class="nota">${esc(b.vazio)}</p>`;
      return `<table class="tabela compacta${b.classe ? ` ${esc(b.classe)}` : ""}"><thead><tr>${b.colunas.map((c) => `<th${c.numero ? ' class="num"' : ""}>${esc(c.titulo)}</th>`).join("")}</tr></thead><tbody>${b.linhas.map((l) => `<tr>${l.celulas.map(celula).join("")}</tr>`).join("")}</tbody></table>${b.mais?.texto ? `<span class="mais">${esc(b.mais.texto)}</span>` : ""}`;
    case "faixas":
      if (!b.faixas.length) return `<p class="nota">${esc(b.vazio)}</p>`;
      return `<ul class="faixas">${b.faixas.map((f) => `<li>${talvez("barra-linha estreita", `<span class="barra-rot">${esc(f.rotulo)}</span><span class="barra-trilho"><span class="barra" style="width:${(f.v / b.max) * 100}%;background:${b.cor}"></span></span><span class="barra-val">${esc(f.texto)}</span>`, "", f.dica)}</li>`).join("")}</ul>`;
    case "ranking": {
      if (!b.itens.length) return `<p class="nota">${esc(b.vazio)}</p>`;
      const max = Math.max(1, ...b.itens.map((f) => f.a + f.b));
      return `<ul class="barras">${b.itens.map((f, i) => `<li>${talvez("barra-linha rank", `<span class="rank-pos">${i + 1}</span><span class="barra-rot">${esc(f.nome)}</span><span class="barra-trilho"><span class="barra" style="width:${(f.a / max) * 100}%;background:${b.cores[0]}"></span>${b.cores[1] && f.b > 0 ? `<span class="barra" style="width:${(f.b / max) * 100}%;background:${b.cores[1]}"></span>` : ""}</span><span class="barra-val">${esc(f.valor)}</span>`, "", f.nome)}</li>`).join("")}</ul>${b.legendas.length > 1 ? `<ul class="dist-legenda">${b.legendas.map((l, i) => `<li><i style="background:${b.cores[i]}"></i>${esc(l)}</li>`).join("")}</ul>` : ""}`;
    }
    case "evolucao":
      return `<p class="nota">A evolução diária aparece a partir das atualizações concluídas (${b.series.map((s) => esc(s.rotulo)).join(", ")}).</p>`;
    default:
      return "";
  }
}

function painelHtml(d, hoje) {
  const blocos = d.blocos.map((b) => b.tipo === "ultima"
    ? `<section class="bloco g4 ultima"><h3>Última atualização</h3><p class="ultima-quando">${dataBR(hoje)} 07:00</p><p class="nota sem-margem">agendada</p></section>`
    : `<section class="bloco g${b.largura}">${b.titulo ? `<h3>${esc(b.titulo)}${b.sub ? ` <span class="n">${esc(b.sub)}</span>` : ""}</h3>` : ""}${conteudo(b)}${b.nota ? `<p class="nota">${esc(b.nota)}</p>` : ""}</section>`).join("");
  return `<h1>${esc(d.titulo)}</h1>${d.texto ? `<p class="sub">${esc(d.texto)}</p>` : ""}<div class="kpis-painel">${d.kpis.map(kpi).join("")}</div><div class="painel-grade">${blocos}</div>`;
}

// ------------------------------------------------------------------ relatório (tabela do plugin)

function valorColuna(c, item, doms) {
  const v = item[c.campo];
  if (v === null || v === undefined || v === "") return esc(c.vazio ?? "");
  const d = c.dominio ? doms[c.dominio] : null;
  if (d) {
    const x = Object.prototype.hasOwnProperty.call(d.valores, String(v)) ? d.valores[String(v)] : null;
    const t = x ? [x.icone, x.rotulo ?? String(v)].filter(Boolean).join(" ") : String(v);
    if (d.estilo === "curva") return `<span class="curva curva-${esc(String(v).toLowerCase())}">${esc(v)}</span>`;
    if (d.estilo === "selo") return `<span class="selo st-${esc(v)}">${esc(t)}</span>`;
    return esc(t);
  }
  if (c.tipo === "data" || c.data) return esc(dataBR(v));
  if (c.tipo === "numero") return num(v, c.casas ?? 0);
  return esc(v);
}

function relatorioHtml(pl, itens, cfg, hoje, limite = 40) {
  const r = pl.relatorio;
  const t = r?.tabela;
  if (!t) return null;
  const ctx = { p: cfg, hoje, dominios: pl.dominios ?? {} };
  const txt = (s) => { try { return textoExpr(String(s ?? ""), { ...ctx, item: {} }); } catch { return String(s ?? ""); } };
  const ord = t.ordem;
  const lista = [...itens];
  if (ord?.campo) lista.sort((a, b) => {
    const x = a[ord.campo], y = b[ord.campo];
    const c = typeof x === "number" && typeof y === "number" ? x - y : String(x ?? "").localeCompare(String(y ?? ""), "pt-BR");
    return ord.desc ? -c : c;
  });
  const cols = t.colunas;
  const linhas = lista.slice(0, limite).map((it) => `<tr>${cols.map((c) => `<td${c.tipo === "numero" ? ' class="num"' : ""}>${valorColuna(c, it, pl.dominios ?? {})}</td>`).join("")}</tr>`).join("");
  const resto = lista.length > limite ? `<p class="nota">Mostrando ${limite} de ${num(lista.length)} linhas do exemplo.</p>` : "";
  return `<h1>${esc(txt(r.titulo ?? pl.nome))}</h1>${r.texto ? `<p class="sub">${esc(txt(r.texto))}</p>` : ""}<section class="bloco"><h3>${esc(txt(t.titulo))} <span class="n">${num(lista.length)} ${esc(pl.itens ?? "itens")}</span></h3><div style="overflow-x:auto"><table class="tabela compacta"><thead><tr>${cols.map((c) => `<th${c.tipo === "numero" ? ' class="num"' : ""}>${esc(txt(c.titulo))}</th>`).join("")}</tr></thead><tbody>${linhas}</tbody></table></div>${resto}</section>`;
}

// ------------------------------------------------------------------ data lab, consolidado, configurações

// Marcações dos textos dos plugins: **negrito**, [[destaque]], `código`.
const rico = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\[\[(.+?)\]\]/g, "<mark>$1</mark>").replace(/`(.+?)`/g, "<code>$1</code>");

function datalabHtml(pl, linhas) {
  const cols = [...new Set(linhas.flatMap((l) => Object.keys(l)))];
  const amostra = linhas.slice(0, 12);
  return `<h1>Relatório do Data Lab: ${esc(pl.dataLab.relatorio)}</h1><p class="sub">O node Waipe Data do flow roda este relatório e o flow envia as linhas ao Waipe Páginas, que reconhece as colunas e calcula.</p>
<section class="bloco"><h3>Texto para criar o relatório</h3><pre style="white-space:pre-wrap;margin:0;font-size:13px;line-height:1.5">${esc(pl.dataLab.texto)}</pre></section>
<section class="bloco" style="margin-top:16px"><h3>Linhas que o relatório devolve <span class="n">${num(linhas.length)} no exemplo</span></h3><div style="overflow-x:auto"><table class="tabela compacta"><thead><tr>${cols.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${amostra.map((l) => `<tr>${cols.map((c) => `<td>${esc(l[c] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
}

function consolidadoHtml(pl, itens, cfg, hoje) {
  const c = pl.consolidado;
  const g = c && pl.grupos?.[c.grupo];
  if (!g) return null;
  const linhas = agrupar(g, itens, cfg, hoje);
  const txt = (s) => { try { return textoExpr(String(s ?? ""), { p: cfg, hoje, dominios: pl.dominios ?? {}, item: { atualizacao: "exemplo" } }); } catch { return String(s ?? ""); } };
  const cols = c.tabela.colunas;
  return `<h1>${esc(txt(c.titulo))}</h1>${c.texto ? `<p class="sub">${rico(txt(c.texto))}</p>` : ""}<section class="bloco"><h3>${esc(txt(c.tabela.titulo))} <span class="n">${num(linhas.length)}</span></h3><div style="overflow-x:auto"><table class="tabela compacta"><thead><tr>${c.tabela.posicao ? "<th>#</th>" : ""}${cols.map((k) => `<th${k.tipo === "numero" ? ' class="num"' : ""}>${esc(txt(k.titulo))}</th>`).join("")}</tr></thead><tbody>${linhas.slice(0, 40).map((l, i) => `<tr>${c.tabela.posicao ? `<td>${i + 1}</td>` : ""}${cols.map((k) => `<td${k.tipo === "numero" ? ' class="num"' : ""}>${valorColuna(k, l, pl.dominios ?? {})}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
}

function configuracoesHtml(pl) {
  const valor = (x) => {
    if (x.tipo === "booleano") return x.padrao ? "Sim" : "Não";
    if (x.tipo === "percentual") return `${num((x.padrao ?? 0) * 100, 1)}%`;
    if (x.tipo === "lista") return esc((x.padrao ?? []).join(", ") || "(vazia)");
    if (x.tipo === "grade") return "tabela por linha";
    return `${esc(typeof x.padrao === "number" ? num(x.padrao, Number.isInteger(x.padrao) ? 0 : 2) : x.padrao ?? "")}${x.sufixo ? ` ${esc(x.sufixo)}` : ""}`;
  };
  const params = (pl.parametros ?? []).map((x) => `<tr><td><b>${esc(x.rotulo)}</b>${x.ajuda ? `<small class="sub">${rico(x.ajuda)}</small>` : ""}</td><td class="num">${valor(x)}</td></tr>`).join("");
  const nomes = { datalab: "📋 Texto do relatório para copiar", id_relatorio: "🔑 Campo para colar o ID do relatório", baixar_flows: "⬇ Baixar os dois flows (agendado e Atualizar pelo Painel)", webhook: "🔗 Campo para colar a URL do webhook", testar: "▶ Testar a atualização" };
  const passos = passosProntos(pl).map((ps, i) => `<li style="margin-bottom:12px"><b>${i + 1}. ${esc(ps.titulo)}</b>${ps.blocos.map((b) => "texto" in b ? `<p style="margin:4px 0">${rico(b.texto)}</p>` : `<p class="nota" style="margin:4px 0">${esc(nomes[b.ferramenta] ?? b.ferramenta)}</p>`).join("")}</li>`).join("");
  return `<h1>Configurações: ${esc(pl.nome)}</h1><p class="sub">O que o cliente ajusta na própria página. Mudar um parâmetro recalcula a base sem esperar o Data Lab.</p>
<section class="bloco"><h3>Parâmetros <span class="n">valores padrão</span></h3><table class="tabela compacta"><thead><tr><th>Parâmetro</th><th class="num">Padrão</th></tr></thead><tbody>${params}</tbody></table></section>
<section class="bloco" style="margin-top:16px"><h3>Integração <span class="n">flow agendado todo dia às ${esc(horario(pl))}</span></h3><ol style="list-style:none;padding:0;margin:0">${passos}</ol></section>`;
}

// ------------------------------------------------------------------ gerar

let falhou = false;
for (const arg of process.argv.slice(2)) {
  const pasta = resolve(arg);
  const slug = basename(pasta);
  try {
    const v = validarPlugin(JSON.parse(readFileSync(join(pasta, `${slug}.json`), "utf8")));
    if (!v.plugin) throw new Error(v.erros.join("; "));
    const pl = v.plugin;
    const linhas = JSON.parse(readFileSync(join(pasta, "exemplo.json"), "utf8"));
    const hoje = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }).format(new Date());
    const cfg = padrao(pl);
    const prep = preparar(pl, linhas, [...new Set(linhas.flatMap((l) => Object.keys(l)))], cfg, hoje);
    if (prep.erro) throw new Error(`exemplo.json: ${prep.erro}`);
    const itens = calcular(pl, prep.itens, cfg, hoje);
    const resumo = resumir(pl, itens, cfg, hoje);
    const d = montarPainel({ plugin: pl, itens, config: cfg, hoje, resumo, dias: [{ dia: hoje, resumo }], ultima: null, atualizacao: "exemplo" });
    const aviso = `<p class="previa-aviso">Prévia com dados fictícios (exemplo.json), calculada pelo motor do Waipe Páginas v${esc(plataforma)}. Na página real os números vêm do Data Lab do cliente.</p>`;
    const dir = join(pasta, "modelos");
    mkdirSync(dir, { recursive: true });
    const pecas = [];
    const gravar = (arquivo, titulo, html, peca) => { writeFileSync(join(dir, arquivo), pagina(titulo, aviso + html)); pecas.push({ arquivo, tipo: "pagina", ...peca }); };
    // Flow que alimenta a página: o mesmo que a página gera em Configurações > Integração (chaves de exemplo).
    const fluxo = montarFlow(pl, "agendado", { apiKey: "SUBSTITUA_PELA_API_KEY_DA_EMPRESA", webhookToken: "", dataLabReportId: "" },
      "https://seu-waipe-paginas.vercel.app", "Empresa Exemplo");
    writeFileSync(join(dir, "fluxo.json"), JSON.stringify(fluxo, null, 2) + "\n");
    gravar("datalab.html", `${pl.nome}: Data Lab`, datalabHtml(pl, linhas), { rotulo: "Relatório do Data Lab", quem: pl.dataLab.relatorio, node: "Waipe Data" });
    gravar("painel.html", `${pl.nome}: Indicadores`, painelHtml(d, hoje), { rotulo: "Indicadores", quem: "Aba Indicadores da página", node: "Finalizar Carga no Painel" });
    const rel = relatorioHtml(pl, itens, cfg, hoje);
    if (rel) gravar("relatorio.html", `${pl.nome}: Relatório`, rel, { rotulo: "Relatório", quem: "Aba Relatório da página" });
    const cons = consolidadoHtml(pl, itens, cfg, hoje);
    if (cons) gravar("consolidado.html", `${pl.nome}: ${pl.consolidado.titulo}`, cons, { rotulo: pl.abas?.consolidado || pl.consolidado.titulo || "Consolidado", quem: "Aba Consolidado da página" });
    gravar("configuracoes.html", `${pl.nome}: Configurações`, configuracoesHtml(pl), { rotulo: "Configurações", quem: "Parâmetros e integração" });
    writeFileSync(join(dir, "modelos.json"), JSON.stringify({ versao: 1, aviso: "Dados fictícios. Desenho e cálculo do plugin no Waipe Páginas.", fluxo: "fluxo.json", pecas }, null, 2) + "\n");
    console.log(`✓ ${slug}: ${pecas.map((p) => p.arquivo).join(", ")} (${itens.length} itens do exemplo)`);
  } catch (e) {
    falhou = true;
    console.log(`✗ ${slug}: ${e instanceof Error ? e.message : e}`);
  }
}
process.exit(falhou ? 1 : 0);
