// Validação completa de plugins com o motor do Waipe Páginas (o mesmo código que roda na instalação e no painel).
// Uso: node .claude/waipe/plugin/validar.mjs <pasta-do-plugin> [...]   (chamado por plugins.py validar)
// Precisa da cópia local do waipe-paginas: variável WAIPE_PAGINAS ou a pasta irmã ../waipe-paginas.
// Para cada plugin: validarPlugin (estrutura, fórmulas, links, cores), configuração padrão válida e o exemplo
// (exemplo.json, dados fictícios do Data Lab) passando por preparar → calcular → resumir → montarPainel.
import { existsSync, readFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const raiz = resolve(import.meta.dirname, "../../..");
const paginas = resolve(process.env.WAIPE_PAGINAS || join(raiz, "..", "waipe-paginas"));
const motorDir = join(paginas, "src/lib/motor");
if (!existsSync(join(motorDir, "motor.ts"))) {
  console.log(JSON.stringify({ semMotor: `Motor não encontrado em ${motorDir}. Clone o waipe-paginas ao lado deste repositório ou defina WAIPE_PAGINAS.` }));
  process.exit(3);
}
const imp = (f) => import(pathToFileURL(join(motorDir, f)).href);
const { validarPlugin } = await imp("validar.ts");
const { calcular, padrao, preparar, resumir, validar } = await imp("motor.ts");
const { montarPainel } = await imp("painel.ts");
const { planejar } = await imp("migracao.ts");
const versao = JSON.parse(readFileSync(join(paginas, "package.json"), "utf8")).version;

const resultado = { plataforma: versao, plugins: {} };
let falhou = false;
for (const pasta of process.argv.slice(2)) {
  const slug = basename(pasta);
  const erros = [];
  const info = {};
  try {
    const json = JSON.parse(readFileSync(join(pasta, `${slug}.json`), "utf8"));
    const v = validarPlugin(json);
    erros.push(...v.erros);
    if (v.plugin) {
      const cfg = padrao(v.plugin);
      erros.push(...validar(v.plugin, cfg).map((e) => `configuração padrão: ${e}`));
      // A instalação num banco vazio precisa planejar sem erro (cria schema e tabela da página).
      erros.push(...planejar(v.plugin, null, null).erros.map((e) => `migração: ${e}`));
      const ex = join(pasta, "exemplo.json");
      if (!existsSync(ex)) erros.push("falta exemplo.json (linhas fictícias do Data Lab).");
      else {
        const linhas = JSON.parse(readFileSync(ex, "utf8"));
        if (!Array.isArray(linhas) || !linhas.length) erros.push("exemplo.json: use uma lista de linhas (objetos coluna → valor).");
        else {
          const hoje = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }).format(new Date());
          const nomes = [...new Set(linhas.flatMap((l) => Object.keys(l)))];
          const prep = preparar(v.plugin, linhas, nomes, cfg, hoje);
          if (prep.erro) erros.push(`exemplo.json: ${prep.erro}`);
          const itens = calcular(v.plugin, prep.itens, cfg, hoje);
          const resumo = resumir(v.plugin, itens, cfg, hoje);
          montarPainel({ plugin: v.plugin, itens, config: cfg, hoje, resumo, dias: [{ dia: hoje, resumo }], ultima: null, atualizacao: "exemplo" });
          info.linhas = linhas.length;
          info.itens = itens.length;
          info.resumo = resumo;
          if (!prep.erro && itens.length === 0) erros.push("exemplo.json: nenhuma linha virou item (todas descartadas?).");
        }
      }
    }
  } catch (e) {
    erros.push(`não foi possível ler ou rodar: ${e instanceof Error ? e.message : e}`);
  }
  if (erros.length) falhou = true;
  resultado.plugins[slug] = { erros, ...info };
}
console.log(JSON.stringify(resultado));
process.exit(falhou ? 1 : 0);
