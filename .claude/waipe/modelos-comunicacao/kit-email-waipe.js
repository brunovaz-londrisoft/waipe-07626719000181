// ============================================================
// PADRÃO DE E-MAIL WAIPE - copie este bloco para o node `code` que monta o e-mail.
// Desenho de referência: o consolidado do gestor do Guardião da Amostra Padrão (claro, com modo escuro automático).
// Marca "waipe" e empresa no topo, cartão branco com faixa escura, título com eyebrow dourado, indicadores
// em verde-oliva, tabelas claras e rodapé Londrisoft. Todo e-mail de agente do Waipe usa este kit.
// As funções devolvem linhas de tabela (<tr>) para dentro do cartão, exceto wpBadge/wpBarra/wpSeta, que devolvem
// HTML para colocar dentro de uma célula. wpPagina devolve o documento HTML completo.
// Compatível com o sandbox do Waipe Flow (sem toLocaleString, sem Intl).
// ============================================================
const WP_F = "font-family:Arial,Helvetica,sans-serif;";

function wpEsc(t) {
  if (t === null || t === undefined) return "";
  return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/'/g, "&#39;");
}
function wpNum(n) { return String(Math.round(Number(n) || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
function wpMoeda(v) {
  const n = Math.round((Number(v) || 0) * 100) / 100;
  const p = Math.abs(n).toFixed(2).split(".");
  return (n < 0 ? "-R$ " : "R$ ") + p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + "," + p[1];
}

// Estilos de destaque (badge, KPI e aviso): fundo, texto e borda. As cores do modo escuro ficam no <style> de wpPagina.
const WP_ESTILOS = {
  neutro: { bg: "#F9FAFB", cor: "#303030", borda: "#E5E7EB" },
  medio: { bg: "#F1F2EC", cor: "#5A6344", borda: "#E3E6D8" },
  forte: { bg: "#5A6344", cor: "#FFFFFF", borda: "#5A6344" },
  alerta: { bg: "#FEF3F2", cor: "#B42318", borda: "#FAD7D3" },
  ok: { bg: "#EEF8F1", cor: "#1E7A45", borda: "#CDEBD7" }
};

// Documento completo: marca e empresa, cartão (eyebrow, título, saudação, destaque), miolo (linhas) e rodapé.
// o: { preheader, empresa, rotuloDireita, eyebrow, titulo, heroEyebrow, heroValor, heroTam, heroSub, heroBarra,
//      heroNota, saudacao, subSaudacao, miolo, rodape: [linhas] }
// eyebrow/titulo são opcionais: sem eles, heroEyebrow vira o eyebrow do cartão.
function wpPagina(o) {
  const eyebrow = o.eyebrow || o.heroEyebrow || "";
  let h = "";
  h += "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>";
  h += "<meta name='color-scheme' content='light dark'><meta name='supported-color-schemes' content='light dark'>";
  h += "<title>" + wpEsc(o.titulo || eyebrow || o.empresa || "Waipe") + "</title>";
  h += "<style>body{margin:0;padding:0;-webkit-text-size-adjust:100%;}a{color:#303030;}";
  h += "@media only screen and (max-width:620px){.wp-wrap{width:100%!important;max-width:100%!important;}.wp-pad{padding-left:16px!important;padding-right:16px!important;}.wp-kpi{display:block!important;width:100%!important;padding:0 0 8px 0!important;}.wp-hide{display:none!important;}.wp-h1{font-size:24px!important;line-height:30px!important;}.wp-hero{font-size:40px!important;line-height:44px!important;}}";
  h += "@media (prefers-color-scheme: dark){.wp-bg{background:#16181D!important;}.wp-card{background:#1F2229!important;border-color:#323743!important;}.wp-soft{background:#272B33!important;}.wp-t{color:#F3F4F6!important;}.wp-m{color:#A8AEBB!important;}.wp-bd{border-color:#323743!important;}.wp-eb{color:#D4B25A!important;}";
  h += "td[bgcolor='#303030']{background:#E5E7EB!important;}td[bgcolor='#303030'] a{color:#1F2229!important;}";
  h += "td[bgcolor='#F9FAFB']{background:#272B33!important;}td[bgcolor='#F1F2EC']{background:#2A2E24!important;}td[bgcolor='#E3E6D8']{background:#3A4030!important;}";
  h += "td[bgcolor='#FEF3F2']{background:#3A2422!important;}td[bgcolor='#EEF8F1']{background:#1F3A2C!important;}td[bgcolor='#F3F4F6']{background:#272B33!important;}";
  h += ".wp-c-medio{color:#C9CFB4!important;}.wp-c-neutro{color:#F3F4F6!important;}.wp-c-alerta{color:#FCA5A5!important;}.wp-c-ok{color:#86EFAC!important;}}";
  h += "</style></head>";
  h += "<body class='wp-bg' style='margin:0;padding:0;background:#F3F4F6;'>";
  h += "<span style='display:none;font-size:1px;color:#F3F4F6;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;'>" + wpEsc(o.preheader || "") + "</span>";
  h += "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' bgcolor='#F3F4F6' class='wp-bg' style='background:#F3F4F6;'><tr><td align='center' style='padding:32px 12px;'>";
  h += "<!--[if mso]><table role='presentation' width='600' cellpadding='0' cellspacing='0' border='0'><tr><td><![endif]-->";
  h += "<table role='presentation' width='600' cellpadding='0' cellspacing='0' border='0' class='wp-wrap' style='width:600px;max-width:600px;'>";
  // Marca
  h += "<tr><td class='wp-pad' style='padding:0 8px 16px 8px;'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr>";
  h += "<td class='wp-t' style='" + WP_F + "font-size:22px;font-weight:bold;color:#303030;letter-spacing:-0.5px;mso-line-height-rule:exactly;line-height:28px;'>waipe</td>";
  h += "<td align='right' class='wp-m' style='" + WP_F + "font-size:12px;color:#6B7280;mso-line-height-rule:exactly;line-height:16px;'>" + wpEsc(o.empresa || "") + (o.rotuloDireita ? "<br>" + o.rotuloDireita : "") + "</td>";
  h += "</tr></table></td></tr>";
  // Cartão
  h += "<tr><td bgcolor='#FEFEFE' class='wp-card' style='background:#FEFEFE;border:1px solid #E5E7EB;border-radius:12px;overflow:hidden;'>";
  h += "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'>";
  h += "<tr><td height='4' bgcolor='#303030' style='height:4px;font-size:0;line-height:0;background:#303030;border-radius:12px 12px 0 0;'>&nbsp;</td></tr>";
  if (eyebrow || o.titulo || o.saudacao) {
    h += "<tr><td class='wp-pad' style='padding:32px 32px 8px 32px;'>";
    if (eyebrow) h += "<p class='wp-eb' style='margin:0 0 8px 0;" + WP_F + "font-size:12px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#8E6A1F;mso-line-height-rule:exactly;line-height:16px;'>" + wpEsc(eyebrow) + "</p>";
    if (o.titulo) h += "<h1 class='wp-h1 wp-t' style='margin:0 0 12px 0;" + WP_F + "font-size:28px;font-weight:bold;color:#303030;letter-spacing:-0.5px;mso-line-height-rule:exactly;line-height:34px;'>" + wpEsc(o.titulo) + "</h1>";
    if (o.saudacao) h += "<p class='wp-t' style='margin:0;" + WP_F + "font-size:15px;color:#303030;mso-line-height-rule:exactly;line-height:23px;'>" + o.saudacao + "</p>";
    if (o.subSaudacao) h += "<p class='wp-m' style='margin:6px 0 0 0;" + WP_F + "font-size:15px;color:#5B6170;mso-line-height-rule:exactly;line-height:23px;'>" + o.subSaudacao + "</p>";
    h += "</td></tr>";
  }
  if (o.heroValor !== undefined && o.heroValor !== null) {
    const tam = Math.min(o.heroTam || 44, 48);
    h += "<tr><td class='wp-pad' style='padding:20px 32px 8px 32px;'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr><td bgcolor='#F1F2EC' style='background:#F1F2EC;border-radius:8px;padding:20px;'>";
    if (o.heroEyebrow && o.eyebrow && o.eyebrow !== o.heroEyebrow) h += "<p class='wp-c-medio' style='margin:0 0 6px 0;" + WP_F + "font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#5A6344;mso-line-height-rule:exactly;line-height:15px;'>" + wpEsc(o.heroEyebrow) + "</p>";
    h += "<p class='wp-hero wp-c-medio' style='margin:0;" + WP_F + "font-size:" + tam + "px;font-weight:bold;color:#5A6344;letter-spacing:-1px;mso-line-height-rule:exactly;line-height:" + (tam + 4) + "px;'>" + wpEsc(o.heroValor) + "</p>";
    if (o.heroSub) h += "<p class='wp-c-medio' style='margin:6px 0 0 0;" + WP_F + "font-size:14px;color:#5A6344;mso-line-height-rule:exactly;line-height:20px;'>" + o.heroSub + "</p>";
    if (o.heroBarra !== undefined && o.heroBarra !== null) {
      const w = Math.max(0, Math.min(100, Math.round(o.heroBarra)));
      h += "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' style='margin-top:14px;'><tr><td bgcolor='#E3E6D8' style='background:#E3E6D8;border-radius:5px;'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr>" +
        "<td width='" + w + "%' height='10' bgcolor='#5A6344' style='height:10px;background:#5A6344;border-radius:5px;font-size:0;line-height:0;'>&nbsp;</td>" +
        (w < 100 ? "<td height='10' style='height:10px;font-size:0;line-height:0;'>&nbsp;</td>" : "") + "</tr></table></td></tr></table>";
    }
    if (o.heroNota) h += "<p class='wp-c-medio' style='margin:10px 0 0 0;" + WP_F + "font-size:12px;color:#5A6344;mso-line-height-rule:exactly;line-height:18px;'>" + o.heroNota + "</p>";
    h += "</td></tr></table></td></tr>";
  }
  h += o.miolo || "";
  h += "<tr><td style='height:24px;font-size:0;line-height:0;'>&nbsp;</td></tr>";
  h += "</table></td></tr>";
  // Rodapé
  const linhasRodape = o.rodape || [];
  h += "<tr><td class='wp-pad' align='center' style='padding:24px 24px 0 24px;'>";
  for (let i = 0; i < linhasRodape.length; i++) {
    h += "<p class='wp-m' style='margin:" + (i > 0 ? "6px" : "0") + " 0 0 0;" + WP_F + "font-size:12px;color:" + (i === linhasRodape.length - 1 ? "#8A90A0" : "#6B7280") + ";mso-line-height-rule:exactly;line-height:18px;'>" + linhasRodape[i] + "</p>";
  }
  h += "</td></tr></table>";
  h += "<!--[if mso]></td></tr></table><![endif]-->";
  h += "</td></tr></table></body></html>";
  return h;
}

// Parágrafo livre (HTML já escapado pelo chamador)
function wpTexto(html) {
  return "<tr><td class='wp-pad' style='padding:8px 32px;'><p class='wp-m' style='margin:0;" + WP_F + "font-size:15px;color:#5B6170;mso-line-height-rule:exactly;line-height:23px;'>" + html + "</p></td></tr>";
}

// Título de seção com subtítulo
function wpSecao(titulo, sub) {
  return "<tr><td class='wp-pad' style='padding:24px 32px 12px 32px;'>" +
    "<p class='wp-t' style='margin:0;" + WP_F + "font-size:16px;font-weight:bold;color:#303030;mso-line-height-rule:exactly;line-height:22px;'>" + wpEsc(titulo) + "</p>" +
    (sub ? "<p class='wp-m' style='margin:4px 0 0 0;" + WP_F + "font-size:12px;color:#6B7280;mso-line-height-rule:exactly;line-height:18px;'>" + sub + "</p>" : "") + "</td></tr>";
}

// Cartões de indicador lado a lado. lista: [{rotulo, valor, estilo, sub}], titulo (opcional) vira um rótulo pequeno acima.
// Sem estilo, o primeiro é "medio" (verde-oliva) e os outros "neutro", como no Guardião.
function wpKpis(lista, titulo) {
  const n = lista.length;
  const larg = (100 / n).toFixed(2);
  let h = "<tr><td class='wp-pad' style='padding:20px 32px 8px 32px;'>";
  if (titulo) h += "<p class='wp-m' style='margin:0 0 8px 0;" + WP_F + "font-size:11px;font-weight:bold;letter-spacing:0.8px;text-transform:uppercase;color:#6B7280;mso-line-height-rule:exactly;line-height:15px;'>" + wpEsc(titulo) + "</p>";
  h += "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr>";
  // Valor longo (ex.: R$ 99.716,16) com 3 ou mais cartões lado a lado: fonte menor para caber numa linha.
  const maiorValor = lista.reduce(function (m, k) { return Math.max(m, String(k.valor === undefined ? "" : k.valor).length); }, 0);
  const tam = n >= 3 && maiorValor > 9 ? 20 : n >= 2 && maiorValor > 14 ? 20 : 26;
  for (let i = 0; i < n; i++) {
    const k = lista[i];
    const nome = WP_ESTILOS[k.estilo] ? k.estilo : (i === 0 ? "medio" : "neutro");
    const e = nome === "forte" ? WP_ESTILOS.medio : WP_ESTILOS[nome];
    const cls = nome === "forte" ? "medio" : nome;
    const pad = n === 1 ? "" : (i === 0 ? "padding-right:6px;" : (i === n - 1 ? "padding-left:6px;" : "padding:0 3px;"));
    h += "<td class='wp-kpi' width='" + larg + "%' valign='top' style='width:" + larg + "%;" + pad + "'>" +
      "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr><td bgcolor='" + e.bg + "' style='background:" + e.bg + ";border-radius:8px;padding:16px;'>" +
      "<p class='wp-c-" + cls + "' style='margin:0;" + WP_F + "font-size:" + tam + "px;font-weight:bold;color:" + e.cor + ";mso-line-height-rule:exactly;line-height:" + (tam + 6) + "px;white-space:nowrap;'>" + wpEsc(k.valor) + "</p>" +
      "<p class='wp-c-" + cls + "' style='margin:4px 0 0 0;" + WP_F + "font-size:13px;color:" + (nome === "neutro" ? "#5B6170" : e.cor) + ";mso-line-height-rule:exactly;line-height:18px;'>" + wpEsc(k.rotulo) + "</p>" +
      (k.sub ? "<p class='wp-m' style='margin:2px 0 0 0;" + WP_F + "font-size:12px;color:#6B7280;mso-line-height-rule:exactly;line-height:16px;'>" + wpEsc(k.sub) + "</p>" : "") +
      "</td></tr></table></td>";
  }
  return h + "</tr></table></td></tr>";
}

// Tabela. colunas: [{t, a: "left"|"right"|"center", w, oculta}], linhas: [[html da célula, ...], ...]
// oculta = some em tela pequena. nota (opcional): texto abaixo da tabela.
function wpTabela(colunas, linhas, nota) {
  let h = "<tr><td class='wp-pad' style='padding:4px 32px 8px 32px;'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' class='wp-bd' style='border:1px solid #E5E7EB;border-radius:8px;border-collapse:separate;'><tr>";
  for (let c = 0; c < colunas.length; c++) {
    const col = colunas[c];
    const canto = c === 0 ? "border-radius:8px 0 0 0;" : (c === colunas.length - 1 ? "border-radius:0 8px 0 0;" : "");
    h += "<td bgcolor='#F9FAFB' align='" + (col.a || "left") + "'" + (col.w ? " width='" + col.w + "'" : "") + " class='wp-soft wp-m" + (col.oculta ? " wp-hide" : "") + "'" +
      " style='background:#F9FAFB;padding:10px 12px;" + WP_F + "font-size:11px;font-weight:bold;letter-spacing:0.8px;text-transform:uppercase;color:#6B7280;mso-line-height-rule:exactly;line-height:15px;" + canto + "'>" + wpEsc(col.t) + "</td>";
  }
  h += "</tr>";
  if (linhas.length === 0) {
    h += "<tr><td colspan='" + colunas.length + "' class='wp-bd wp-m' style='border-top:1px solid #F3F4F6;padding:14px 12px;" + WP_F + "font-size:13px;color:#6B7280;'>Nada para mostrar.</td></tr>";
  }
  for (let i = 0; i < linhas.length; i++) {
    h += "<tr>";
    for (let c = 0; c < colunas.length; c++) {
      const col = colunas[c];
      h += "<td" + (col.a ? " align='" + col.a + "'" : "") + " valign='middle' class='wp-bd wp-t" + (col.oculta ? " wp-hide" : "") + "'" +
        " style='border-top:1px solid #F3F4F6;padding:10px 12px;" + WP_F + "font-size:13px;color:#303030;mso-line-height-rule:exactly;line-height:18px;'>" + (linhas[i][c] === undefined ? "" : linhas[i][c]) + "</td>";
    }
    h += "</tr>";
  }
  h += "</table>" + (nota ? "<p class='wp-m' style='margin:8px 2px 0 2px;" + WP_F + "font-size:12px;color:#6B7280;mso-line-height-rule:exactly;line-height:17px;'>" + nota + "</p>" : "") + "</td></tr>";
  return h;
}

// Pílula de destaque (para dentro de uma célula). a: "left" | "right". Texto curto (até 3 caracteres) vira círculo,
// como a posição do ranking do Guardião.
function wpBadge(texto, estilo, a) {
  const nome = WP_ESTILOS[estilo] ? estilo : "neutro";
  const e = nome === "neutro" ? { bg: "#F3F4F6", cor: "#5B6170" } : WP_ESTILOS[nome];
  const t = String(texto === null || texto === undefined ? "" : texto);
  const alinhar = a === "right" ? " align='right'" : "";
  if (t.length <= 3) {
    return "<table role='presentation' cellpadding='0' cellspacing='0' border='0'" + alinhar + "><tr><td width='24' height='24' align='center' valign='middle' bgcolor='" + e.bg + "' style='width:24px;height:24px;background:" + e.bg + ";border-radius:12px;" + WP_F + "font-size:12px;font-weight:bold;color:" + e.cor + ";mso-line-height-rule:exactly;line-height:24px;'>" + wpEsc(t) + "</td></tr></table>";
  }
  return "<table role='presentation' cellpadding='0' cellspacing='0' border='0'" + alinhar + "><tr><td bgcolor='" + e.bg + "' style='background:" + e.bg + ";border-radius:20px;padding:3px 10px;" + WP_F + "font-size:11px;font-weight:bold;color:" + e.cor + ";white-space:nowrap;mso-line-height-rule:exactly;line-height:16px;'>" + wpEsc(t) + "</td></tr></table>";
}

// Barra proporcional (para dentro de uma célula). pct 0-100; forte = verde-oliva cheio, senão oliva claro
function wpBarra(pct, forte) {
  const w = Math.max(4, Math.min(100, Math.round(pct)));
  const cor = forte ? "#5A6344" : "#BFC4AC";
  return "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' style='margin-top:6px;'><tr>" +
    "<td width='" + w + "%' height='6' bgcolor='" + cor + "' style='height:6px;background:" + cor + ";border-radius:3px;font-size:0;line-height:0;'>&nbsp;</td>" +
    (w < 100 ? "<td width='" + (100 - w) + "%' height='6' style='height:6px;font-size:0;line-height:0;'>&nbsp;</td>" : "") + "</tr></table>";
}

// Botão quadrado com seta (para dentro de uma célula): abre a planilha ou lista da linha
function wpSeta(url, titulo) {
  return "<table role='presentation' cellpadding='0' cellspacing='0' border='0' align='right'><tr><td width='32' height='32' align='center' valign='middle' bgcolor='#303030' style='width:32px;height:32px;background:#303030;border-radius:8px;'>" +
    "<a href='" + wpEsc(url) + "' target='_blank' title='" + wpEsc(titulo) + "' aria-label='" + wpEsc(titulo) + "' style='display:block;width:32px;" + WP_F + "font-size:18px;font-weight:bold;color:#FFFFFF;text-decoration:none;mso-line-height-rule:exactly;line-height:32px;border-radius:8px;'>&rarr;</a></td></tr></table>";
}

// Botão de chamada (linha própria)
function wpBotao(url, rotulo) {
  return "<tr><td class='wp-pad' align='left' style='padding:16px 32px 8px 32px;'><table role='presentation' cellpadding='0' cellspacing='0' border='0'><tr><td align='center' bgcolor='#303030' style='background:#303030;border-radius:8px;'>" +
    "<a href='" + wpEsc(url) + "' target='_blank' style='display:block;padding:12px 24px;" + WP_F + "font-size:14px;font-weight:bold;color:#FFFFFF;text-decoration:none;mso-line-height-rule:exactly;line-height:20px;border-radius:8px;'>" + wpEsc(rotulo) + "</a></td></tr></table></td></tr>";
}

// Caixa de aviso (linha própria): titulo + corpo em HTML
function wpAviso(titulo, corpoHtml, estilo) {
  const nome = WP_ESTILOS[estilo] ? estilo : "medio";
  const e = nome === "forte" ? WP_ESTILOS.medio : WP_ESTILOS[nome];
  const cls = nome === "forte" ? "medio" : nome;
  return "<tr><td class='wp-pad' style='padding:16px 32px 8px 32px;'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'><tr><td bgcolor='" + e.bg + "' style='background:" + e.bg + ";border:1px solid " + e.borda + ";border-radius:8px;padding:16px 18px;'>" +
    "<p class='wp-c-" + cls + "' style='margin:0;" + WP_F + "font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:" + e.cor + ";mso-line-height-rule:exactly;line-height:16px;'>" + wpEsc(titulo) + "</p>" +
    "<p class='wp-t' style='margin:8px 0 0 0;" + WP_F + "font-size:13px;color:#303030;mso-line-height-rule:exactly;line-height:20px;'>" + corpoHtml + "</p></td></tr></table></td></tr>";
}
// ============================================================
// FIM DO PADRÃO DE E-MAIL WAIPE
// ============================================================
