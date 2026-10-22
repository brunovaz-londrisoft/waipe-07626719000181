// Roda um node `code` de um flow do Waipe com entradas fictícias e imprime a saída em JSON.
// Serve para gerar os modelos de comunicação a partir do código real do node (o e-mail do modelo é
// exatamente o que o node monta), sem rodar o flow nem chamar o Data Lab.
//
// Uso: node rodar-node.mjs <flow.json> "<nome do node>" <entradas.json>
// entradas.json: { "items": [{"json": {...}}], "node": {"Nome de outro node": {...json...}}, "json": {...}, "hoje": "2026-10-20" }
//   items = entrada do node (modo all_items); json = item atual (modo each_item);
//   node  = saídas de outros nodes lidas com $node["Nome"].json; hoje = valor de $today (AAAA-MM-DD)
// Saída: o array devolvido pelo node (cada item com .json), em JSON no stdout. console.log do node vai para o stderr.
import { readFileSync } from "node:fs";

const [flowPath, nomeNode, entradasPath] = process.argv.slice(2);
if (!flowPath || !nomeNode || !entradasPath) {
  console.error('uso: node rodar-node.mjs <flow.json> "<nome do node>" <entradas.json>');
  process.exit(2);
}
const flow = JSON.parse(readFileSync(flowPath, "utf8"));
const node = flow.nodes.find((n) => n.name === nomeNode);
if (!node || node.type !== "code") {
  console.error(`node code "${nomeNode}" não encontrado em ${flowPath}`);
  process.exit(2);
}
const entradas = JSON.parse(readFileSync(entradasPath, "utf8"));
const $node = new Proxy(
  {},
  {
    get(_, nome) {
      if (!(nome in (entradas.node || {}))) throw new Error(`entradas.json não tem a saída do node "${String(nome)}"`);
      return { json: entradas.node[nome] };
    },
  },
);
const items = entradas.items || [];
const $json = entradas.json || (items[0] && items[0].json) || {};
const $today = entradas.hoje || new Date().toISOString().slice(0, 10);
const $now = entradas.agora || $today + "T07:00:00-03:00";
const consoleNode = { log: (...a) => console.error("[node]", ...a), warn: (...a) => console.error("[node]", ...a), error: (...a) => console.error("[node]", ...a) };

const executar = new Function("items", "$node", "$json", "$input", "$today", "$now", "console", node.parameters.jsCode);
const saida = executar(items, $node, $json, { all: () => items, first: () => items[0] }, $today, $now, consoleNode);
process.stdout.write(JSON.stringify(saida, null, 2));
