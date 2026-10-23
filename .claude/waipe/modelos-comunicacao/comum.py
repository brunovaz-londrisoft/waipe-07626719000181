# -*- coding: utf-8 -*-
"""Peças dos modelos de comunicação: só o que é enviado, sem moldura de apresentação.

- E-mail: o HTML que o node monta, gerado rodando o próprio node com dados fictícios (rodar_node).
- WhatsApp: pagina_whatsapp() desenha só a conversa, com o texto igual ao do node.
- Planilha: pagina_planilha() desenha só a planilha, no estilo do Google Sheets.
- Documento: o PDF, impresso pelo navegador sem janela (ver PADRAO.md).

Toda peça segue o tema do sistema (prefers-color-scheme), como os e-mails. O portal de modelos troca o tema e
desenha a moldura (cliente de e-mail, celular) a partir do modelos.json da pasta (salvar_manifesto).
Tudo autocontido, sem recursos externos."""
import html as _h, json, os, re, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))


def esc(t):
    return _h.escape(str(t), quote=True)


def moeda(v):
    s = '{:,.2f}'.format(abs(v)).replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('-R$ ' if v < 0 else 'R$ ') + s


def moeda_abrev(v):
    a = abs(v)
    if a >= 1000000:
        return 'R$ ' + ('%.1f' % (a / 1000000)).replace('.', ',') + ' mi'
    if a >= 1000:
        return 'R$ %d mil' % round(a / 1000)
    return moeda(v)


def pct(v):
    return ('%.1f' % v).replace('.', ',')


def gravar(pasta, rel, conteudo):
    """Grava uma peça em <pasta>/<rel> (texto ou bytes)."""
    caminho = os.path.join(pasta, rel)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    modo = 'wb' if isinstance(conteudo, bytes) else 'w'
    with open(caminho, modo, **({} if modo == 'wb' else {'encoding': 'utf-8'})) as f:
        f.write(conteudo)
    return caminho


def rodar_node(flow, nome_node, entradas):
    """Roda um node `code` do flow com entradas fictícias (ver rodar-node.mjs) e devolve a lista de itens .json."""
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as t:
        json.dump(entradas, t, ensure_ascii=False)
    try:
        r = subprocess.run(['node', os.path.join(AQUI, 'rodar-node.mjs'), flow, nome_node, t.name],
                           capture_output=True, text=True)
    finally:
        os.unlink(t.name)
    if r.returncode != 0:
        raise RuntimeError('node "%s" falhou:\n%s' % (nome_node, r.stderr))
    saida = json.loads(r.stdout)
    if isinstance(saida, dict):  # modo each_item devolve um item só
        saida = [saida]
    return [i.get('json', i) for i in saida]


def salvar_manifesto(pasta, pecas):
    """Grava <pasta>/modelos.json, a lista das peças que o portal mostra, na ordem dada.
    Cada peça: {arquivo, tipo: email|whatsapp|planilha|documento, rotulo, para, ...}
      email:     assunto, de ("Nome <email>"), data
      whatsapp:  contato (nome que aparece no topo da conversa), data
      planilha / documento: só arquivo, tipo, rotulo e, se quiser, para."""
    for p in pecas:
        if not os.path.exists(os.path.join(pasta, p['arquivo'])):
            raise FileNotFoundError('peça sem arquivo: %s' % p['arquivo'])
    dados = {'versao': 1, 'aviso': 'Dados fictícios. O layout, os textos e a ordem seguem o que o fluxo envia.', 'pecas': pecas}
    gravar(pasta, 'modelos.json', json.dumps(dados, ensure_ascii=False, indent=2) + '\n')


# ------------------------------------------------------------------ WhatsApp (só a conversa)
CSS_ZAP = """
:root{--bg:#efeae2;--head:#f0f2f5;--headtx:#111b21;--bub:#fff;--tx:#111b21;--mut:#667781;--card:#f0f2f5;--data:#fff;--link:#027eb5;--pad:rgba(0,0,0,.035)}
@media (prefers-color-scheme: dark){:root{--bg:#0b141a;--head:#202c33;--headtx:#e9edef;--bub:#202c33;--tx:#e9edef;--mut:#8696a0;--card:#182229;--data:#182229;--link:#53bdeb;--pad:rgba(255,255,255,.025)}}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--tx);font-family:"Segoe UI",Helvetica,Arial,sans-serif;display:flex;flex-direction:column}
.zh{background:var(--head);color:var(--headtx);display:flex;align-items:center;gap:12px;padding:10px 16px;flex:none}
.zh .av{width:40px;height:40px;border-radius:50%;background:#25d366;color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:15px}
.zh .nm{font-weight:600;font-size:16px;line-height:20px}.zh .st{font-size:13px;color:var(--mut)}
.zc{flex:1;overflow:auto;padding:16px 6% 24px;background-image:radial-gradient(var(--pad) 1.2px,transparent 1.2px);background-size:16px 16px}
.zdata{margin:4px auto 14px;width:max-content;background:var(--data);color:var(--mut);font-size:12.5px;padding:5px 12px;border-radius:8px;box-shadow:0 1px .5px rgba(0,0,0,.13);text-transform:uppercase}
.zmsg{max-width:min(560px,86%);background:var(--bub);color:var(--tx);border-radius:0 8px 8px 8px;padding:6px 9px 6px;margin:0 0 10px;font-size:14.5px;line-height:20px;box-shadow:0 1px .5px rgba(0,0,0,.13);animation:zin .3s ease both;overflow-wrap:anywhere}
.zmsg .hr{font-size:11px;color:var(--mut);text-align:right;margin-top:2px}
.zmsg .hr i{color:#53bdeb;font-style:normal;margin-left:3px}
.zdoc{display:flex;gap:10px;align-items:center;background:var(--card);border-radius:6px;padding:10px;margin-bottom:6px;cursor:pointer;border:0;width:100%;text-align:left;font:inherit;color:inherit;text-decoration:none}
.zdoc .pdf{width:36px;height:42px;border-radius:4px;background:#e5463d;color:#fff;font-weight:700;font-size:11px;display:flex;align-items:flex-end;justify-content:center;padding-bottom:5px;flex:none}
.zdoc .n{font-size:14px;line-height:18px;font-weight:600;overflow-wrap:anywhere}.zdoc .m{font-size:12px;color:var(--mut)}
.zlink{display:block;text-decoration:none;color:inherit;background:var(--card);border-radius:6px;overflow:hidden;margin-bottom:6px}
.zlink .th{height:70px;background:linear-gradient(135deg,#1e8e3e,#34a853);display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px}
.zlink .tx{padding:8px 10px}.zlink .t{font-weight:600;font-size:14px;line-height:18px}.zlink .h{font-size:12px;color:var(--mut)}
.zmsg a.url{color:var(--link)}
.ztype{display:flex;gap:4px;background:var(--bub);border-radius:0 8px 8px 8px;padding:12px 14px;width:max-content;margin:0 0 10px;box-shadow:0 1px .5px rgba(0,0,0,.13)}
.ztype i{width:7px;height:7px;border-radius:50%;background:var(--mut);animation:zt 1s infinite}.ztype i:nth-child(2){animation-delay:.15s}.ztype i:nth-child(3){animation-delay:.3s}
@keyframes zt{0%,60%,100%{opacity:.3;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}
@keyframes zin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){.zmsg{animation:none}.ztype i{animation:none}}
"""

JS_ZAP = """
var MSGS=%(msgs)s, HORA=%(hora)s, DATA=%(data)s, LINKS=%(links)s;
function formata(t){
  t=t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  t=t.replace(/(https?:\\/\\/[^\\s<]+)/g,function(u){return '<a class="url" href="'+(LINKS[u]||u)+'" target="_blank" rel="noopener">'+u+'</a>';});
  t=t.replace(/\\*([^*\\n]+)\\*/g,'<b>$1</b>').replace(/(^|[\\s(])_([^_\\n]+)_(?=[\\s).,]|$)/g,'$1<i>$2</i>').replace(/~([^~\\n]+)~/g,'<s>$1</s>');
  return t.replace(/\\n/g,'<br>');
}
function balao(m){
  var h='';
  if(m.doc){h+='<a class="zdoc" href="'+m.doc.href+'" target="_blank" rel="noopener"><span class="pdf">PDF</span><span><div class="n">'+m.doc.nome+'</div><div class="m">'+(m.doc.meta||'PDF')+'</div></span></a>';}
  if(m.link){h+='<a class="zlink" href="'+m.link.href+'" target="_blank" rel="noopener"><div class="th">&#9638;</div><div class="tx"><div class="t">'+m.link.titulo+'</div><div class="h">'+m.link.host+'</div></div></a>';}
  return h+formata(m.texto||'')+'<div class="hr">'+HORA+'<i>&#10003;&#10003;</i></div>';
}
var chat=document.getElementById('chat'), animando=0;
function tocar(animar){
  var id=++animando;chat.innerHTML='<div class="zdata">'+DATA+'</div>';var i=0;
  if(!animar){MSGS.forEach(function(m){var b=document.createElement('div');b.className='zmsg';b.style.animation='none';b.innerHTML=balao(m);chat.appendChild(b);});return;}
  (function prox(){
    if(id!==animando||i>=MSGS.length)return;var m=MSGS[i++];
    var d=document.createElement('div');d.className='ztype';d.innerHTML='<i></i><i></i><i></i>';chat.appendChild(d);chat.scrollTop=chat.scrollHeight;
    setTimeout(function(){if(id!==animando)return;d.remove();var b=document.createElement('div');b.className='zmsg';b.innerHTML=balao(m);chat.appendChild(b);setTimeout(prox,600);},900);
  })();
}
window.addEventListener('message',function(e){if(e.data&&e.data.waipe==='repetir')tocar(true);});
tocar(!/[?&]estatico\\b/.test(location.search));
"""


def pagina_whatsapp(mensagens, contato, hora='07:00', data='HOJE', links=None, titulo='WhatsApp'):
    """Só a conversa. mensagens: [{texto, doc?: {nome, meta, href}, link?: {titulo, host, href}}], com o texto IGUAL
    ao do node (*negrito*, _itálico_, quebras de linha). links: {url que aparece no texto: arquivo local}.
    ?estatico na URL mostra tudo sem animação; o portal pede "repetir" por postMessage."""
    ini = ''.join(p[0] for p in re.findall(r'[A-Za-zÀ-ú]+', contato)[:2]).upper() or 'W'
    js = JS_ZAP % dict(msgs=json.dumps(mensagens, ensure_ascii=False).replace('</', '<\\/'), hora=json.dumps(hora),
                       data=json.dumps(data, ensure_ascii=False), links=json.dumps(links or {}, ensure_ascii=False))
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="color-scheme" content="light dark"><title>%s</title><style>%s</style></head><body>'
            '<div class="zh"><div class="av">%s</div><div><div class="nm">%s</div><div class="st">online</div></div></div>'
            '<div class="zc" id="chat"></div><script>%s</script></body></html>') % (esc(titulo), CSS_ZAP, esc(ini), esc(contato), js)


# ------------------------------------------------------------------ Planilha (só a planilha, estilo Google Sheets)
CSS_PLANILHA = """
:root{--bg:#fff;--bd:#e1e3e6;--tx:#202124;--mut:#5f6368;--hd:#f8f9fa;--sel:#e8f0fe;--ac:#188038}
@media (prefers-color-scheme: dark){:root{--bg:#1f1f1f;--bd:#3c4043;--tx:#e8eaed;--mut:#9aa0a6;--hd:#28292c;--sel:#253247;--ac:#81c995}}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--tx);font-family:Arial,Helvetica,sans-serif;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--bd);flex:none}
.ico{width:22px;height:28px;background:var(--ac);border-radius:3px;position:relative;flex:none}
.ico:after{content:"";position:absolute;inset:8px 5px 6px;border:2px solid var(--bg);border-radius:1px}
.top .t{font-size:16px;line-height:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.area{flex:1;overflow:auto}
table{border-collapse:separate;border-spacing:0;font-size:13px;table-layout:fixed}
th{background:var(--hd);color:var(--mut);font-weight:400;border-right:1px solid var(--bd);border-bottom:1px solid var(--bd);padding:4px;position:sticky;top:0;z-index:1;height:24px}
td{border-right:1px solid var(--bd);border-bottom:1px solid var(--bd);padding:4px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;height:26px}
td.rn,th.rn{width:46px;background:var(--hd);color:var(--mut);text-align:center;padding:4px;position:sticky;left:0;z-index:2}
th.rn{z-index:3}
tr.h td{font-weight:700;background:var(--sel)}td.num{text-align:right;font-variant-numeric:tabular-nums}
.abas{display:flex;align-items:center;gap:6px;padding:6px 12px;border-top:1px solid var(--bd);background:var(--hd);font-size:13px;flex:none}
.abas .a{background:var(--sel);color:#1a73e8;font-weight:700;padding:6px 14px;border-radius:4px}
@media (prefers-color-scheme: dark){.abas .a{color:#8ab4f8}}
"""


def ler_planilha(caminho):
    """Lê de volta uma planilha gerada por pagina_planilha: (titulo, colunas, linhas, aba). Serve de fonte dos dados
    fictícios ao regerar os modelos (os números voltam como int/float)."""
    s = open(caminho, encoding='utf-8').read()
    titulo = _h.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    aba = _h.unescape(re.search(r'<span class="a">(.*?)</span>', s).group(1))
    corpo = s.split('<tbody>')[1].split('</tbody>')[0]
    linhas = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', corpo, re.S):
        celulas = re.findall(r'<td([^>]*)>(.*?)</td>', tr, re.S)[1:]
        linha = []
        for attr, v in celulas:
            v = _h.unescape(v)
            if 'num' in attr:
                try:
                    v = int(v) if re.fullmatch(r'-?\d+', v) else float(v)
                except ValueError:
                    pass
            linha.append(v)
        linhas.append(linha)
    return titulo, linhas[0], linhas[1:], aba


def pagina_planilha(titulo, colunas, linhas, aba='Página1', larguras=None):
    """Só a planilha: título, grade com letras e números e a aba. Números (int/float) ficam alinhados à direita."""
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    larguras = larguras or [180] * len(colunas)
    cols = '<col style="width:46px">' + ''.join('<col style="width:%dpx">' % w for w in (larguras + [160] * len(colunas))[:len(colunas)])
    cab = '<th class="rn"></th>' + ''.join('<th>%s</th>' % letras[i % 26] for i in range(len(colunas)))
    corpo = '<tr class="h"><td class="rn">1</td>' + ''.join('<td>%s</td>' % esc(c) for c in colunas) + '</tr>'
    for n, l in enumerate(linhas, start=2):
        corpo += '<tr><td class="rn">%d</td>' % n + ''.join(
            '<td%s>%s</td>' % (' class="num"' if isinstance(v, (int, float)) else '', esc(v)) for v in l) + '</tr>'
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="color-scheme" content="light dark"><title>%(t)s</title><style>%(css)s</style></head><body>'
            '<div class="top"><span class="ico"></span><span class="t">%(t)s</span></div>'
            '<div class="area"><table><colgroup>%(cols)s</colgroup><thead><tr>%(cab)s</tr></thead><tbody>%(corpo)s</tbody></table></div>'
            '<div class="abas"><span class="a">%(aba)s</span></div></body></html>') % dict(
        t=esc(titulo), css=CSS_PLANILHA, cols=cols, cab=cab, corpo=corpo, aba=esc(aba))


# ------------------------------------------------------------------ Geradores por modelo (gerar_modelos.py)
def modelo_do_arquivo(arquivo):
    """Para o gerar_modelos.py de um modelo/agente: (slug, caminho do flow, pasta modelos/)."""
    pasta = os.path.dirname(os.path.abspath(arquivo))
    slug = os.path.basename(pasta)
    return slug, os.path.join(pasta, slug + '.json'), os.path.join(pasta, 'modelos')


def slug_de(nome):
    """'Otávio Brandão' -> 'otavio-brandao' (nome de arquivo)."""
    import unicodedata
    t = unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def planilhas_salvas(saida):
    """Relê as planilhas já salvas em <saida>/planilhas/ (a fonte das listas fictícias) e as redesenha com o
    pagina_planilha atual. Devolve [(arquivo relativo, titulo, colunas, linhas)], em ordem de nome."""
    pasta = os.path.join(saida, 'planilhas')
    out = []
    for nome in sorted(os.listdir(pasta)) if os.path.isdir(pasta) else []:
        if not nome.endswith('.html'):
            continue
        caminho = os.path.join(pasta, nome)
        larguras = [int(w) for w in re.findall(r'<col style="width:(\d+)px">', open(caminho, encoding='utf-8').read())[1:]]
        titulo, colunas, linhas, aba = ler_planilha(caminho)
        gravar(saida, 'planilhas/' + nome, pagina_planilha(titulo, colunas, linhas, aba, larguras))
        out.append(('planilhas/' + nome, titulo, colunas, linhas))
    return out


def nome_na_planilha(titulo):
    """'Radar do Primeiro Pedido - Helena Prado - 20-10-2026' -> 'Helena Prado'."""
    partes = titulo.split(' - ')
    return partes[1] if len(partes) >= 3 else titulo
