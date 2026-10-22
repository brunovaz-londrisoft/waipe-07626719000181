# -*- coding: utf-8 -*-
"""Peças visuais comuns: página base, WhatsApp interativo, visualizador de e-mail, planilha. Tudo autocontido (sem recursos externos)."""
import html as _h, json, re

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

CSS_BASE = """
:root{--bg:#eef0f3;--card:#ffffff;--tx:#1f2430;--mut:#6b7280;--bd:#e3e6ea;--acc:#303030;--acc-tx:#fff;--chip:#f1f2ec;--chip-tx:#5a6344;--shadow:0 10px 40px rgba(20,24,40,.12)}
:root[data-tema=dark]{--bg:#0f1115;--card:#171a21;--tx:#eceef2;--mut:#9aa1ad;--bd:#262b35;--acc:#e5e7eb;--acc-tx:#1f2229;--chip:#242a1f;--chip-tx:#c9cfb4;--shadow:0 10px 40px rgba(0,0,0,.5)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;min-height:100vh}
a{color:inherit}
.topo{max-width:1180px;margin:0 auto;padding:22px 20px 0;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.topo .voltar{font-size:14px;text-decoration:none;color:var(--mut);padding:7px 12px;border:1px solid var(--bd);border-radius:999px;background:var(--card)}
.topo .voltar:hover{color:var(--tx)}
.marca{font-weight:800;letter-spacing:-.5px;font-size:20px}
.espaco{flex:1}
.btn{font:inherit;font-size:14px;border:1px solid var(--bd);background:var(--card);color:var(--tx);padding:8px 14px;border-radius:999px;cursor:pointer}
.btn:hover{border-color:var(--mut)}
.btn.pri{background:var(--acc);color:var(--acc-tx);border-color:var(--acc)}
.fake{max-width:1180px;margin:14px auto 0;padding:0 20px}
.fake span{display:inline-block;font-size:12px;color:var(--mut);background:var(--card);border:1px dashed var(--bd);padding:5px 10px;border-radius:8px}
html,body{overflow-x:hidden}.layout>div{min-width:0}.mail{max-width:100%}.layout{max-width:1180px;margin:0 auto;padding:22px 20px 60px;display:grid;grid-template-columns:minmax(260px,380px) 1fr;gap:40px;align-items:start}
@media(max-width:900px){.layout{grid-template-columns:1fr;gap:24px}}
.info h1{font-size:30px;line-height:36px;margin:6px 0 10px;letter-spacing:-.6px}
.info p{color:var(--mut);line-height:24px;margin:0 0 16px}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#8e6a1f}
:root[data-tema=dark] .eyebrow{color:#d4b25a}
.chips{display:flex;flex-direction:column;gap:8px;margin:18px 0}
.chip{display:flex;gap:10px;align-items:flex-start;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:11px 13px;font-size:14px;line-height:20px}
.chip b{display:block;font-size:11px;letter-spacing:.9px;text-transform:uppercase;color:var(--mut);margin-bottom:1px}
.chip .ic{font-size:18px;line-height:22px}
.acoes{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.dica{font-size:13px;color:var(--mut);margin-top:14px}
"""

JS_TEMA = """
(function(){try{var t=localStorage.getItem('tema');if(t)document.documentElement.setAttribute('data-tema',t);}catch(e){}})();
function alternarTema(){var r=document.documentElement;var n=r.getAttribute('data-tema')==='dark'?'light':'dark';r.setAttribute('data-tema',n);try{localStorage.setItem('tema',n)}catch(e){}if(window.aoMudarTema)window.aoMudarTema(n);}
"""

def pagina(titulo, topo_voltar, eyebrow, h1, descricao, chips, miolo, extra_css='', extra_js='', acoes_extra=''):
    chips_html = ''.join('<div class="chip"><span class="ic">%s</span><div><b>%s</b>%s</div></div>' % (i, esc(k), v) for i, k, v in chips)
    return """<!doctype html>
<html lang="pt-BR" data-tema="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titulo)s</title><style>%(css)s%(extra_css)s</style><script>%(js_tema)s</script></head><body>
<div class="topo"><a class="voltar" href="%(voltar)s">&larr; Voltar</a><span class="marca">waipe</span><span class="espaco"></span>%(acoes_extra)s<button class="btn" onclick="alternarTema()">Claro / escuro</button></div>
<div class="fake"><span>Modelo para apresentação &middot; todos os nomes, telefones, e-mails e valores são fictícios</span></div>
<div class="layout">
<div class="info"><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1><p>%(desc)s</p><div class="chips">%(chips)s</div></div>
<div>%(miolo)s</div></div>
<script>%(extra_js)s</script></body></html>""" % dict(titulo=esc(titulo), css=CSS_BASE, extra_css=extra_css, js_tema=JS_TEMA, voltar=topo_voltar,
                                                       acoes_extra=acoes_extra, eyebrow=esc(eyebrow), h1=esc(h1), desc=descricao, chips=chips_html,
                                                       miolo=miolo, extra_js=extra_js)

# ------------------------------------------------------------------ WhatsApp
CSS_ZAP = """
.fone{width:392px;max-width:100%;margin:0 auto;background:#111;border-radius:42px;padding:11px;box-shadow:var(--shadow)}
.tela{border-radius:32px;overflow:hidden;height:760px;display:flex;flex-direction:column;background:var(--zbg);position:relative;
 --zbg:#ece5dd;--zhead:#075e54;--zbub:#ffffff;--ztx:#111b21;--zmut:#667781;--zdoc:#f0f2f5;--zbar:#f0f2f5;--zdata:#e1f2fb;--zdatatx:#54656f}
:root[data-tema=dark] .tela{--zbg:#0b141a;--zhead:#1f2c34;--zbub:#202c33;--ztx:#e9edef;--zmut:#8696a0;--zdoc:#182229;--zbar:#1f2c34;--zdata:#182229;--zdatatx:#8696a0}
.zh{background:var(--zhead);color:#fff;display:flex;align-items:center;gap:10px;padding:34px 12px 10px}
.zh .av{width:38px;height:38px;border-radius:50%;background:#dfe5e7;color:#075e54;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:14px}
.zh .nm{font-weight:600;font-size:16px;line-height:19px}.zh .st{font-size:12px;opacity:.8}
.zc{position:relative;flex:1;overflow:auto;padding:12px 10px;background-image:radial-gradient(rgba(0,0,0,.04) 1px,transparent 1px);background-size:14px 14px}
.zdata{margin:4px auto 12px;width:max-content;background:var(--zdata);color:var(--zdatatx);font-size:12px;padding:5px 11px;border-radius:8px}
.zmsg{max-width:88%;background:var(--zbub);color:var(--ztx);border-radius:0 10px 10px 10px;padding:7px 9px 5px;margin:0 0 8px;font-size:14.5px;line-height:20px;box-shadow:0 1px .5px rgba(0,0,0,.13);animation:zin .35s ease both;word-wrap:break-word}
.zmsg .hr{font-size:11px;color:var(--zmut);text-align:right;margin-top:2px}
.zmsg b{font-weight:700}
.zdoc{display:flex;gap:10px;align-items:center;background:var(--zdoc);border-radius:8px;padding:10px;margin-bottom:6px;cursor:pointer;border:0;width:100%;text-align:left;font:inherit;color:inherit}
.zdoc:hover{filter:brightness(.97)}
.zdoc .pdf{width:40px;height:46px;border-radius:5px;background:#e5463d;color:#fff;font-weight:800;font-size:12px;display:flex;align-items:flex-end;justify-content:center;padding-bottom:6px;flex:none}
.zdoc .n{font-size:14px;line-height:18px;font-weight:600;word-break:break-all}.zdoc .m{font-size:12px;color:var(--zmut)}
.zlink{display:block;text-decoration:none;color:inherit;background:var(--zdoc);border-radius:8px;overflow:hidden;margin-bottom:6px}
.zlink .th{height:74px;background:linear-gradient(135deg,#1e8e3e,#34a853);display:flex;align-items:center;justify-content:center;color:#fff;font-size:34px}
.zlink .tx{padding:8px 10px}.zlink .t{font-weight:600;font-size:14px;line-height:18px}.zlink .h{font-size:12px;color:var(--zmut)}
.zmsg a.url{color:#027eb5;word-break:break-all}
:root[data-tema=dark] .zmsg a.url{color:#53bdeb}
.ztype{display:flex;gap:4px;background:var(--zbub);border-radius:0 10px 10px 10px;padding:12px 14px;width:max-content;margin:0 0 8px;box-shadow:0 1px .5px rgba(0,0,0,.13)}
.ztype i{width:7px;height:7px;border-radius:50%;background:var(--zmut);animation:zt 1s infinite}.ztype i:nth-child(2){animation-delay:.15s}.ztype i:nth-child(3){animation-delay:.3s}
@keyframes zt{0%,60%,100%{opacity:.3;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}
@keyframes zin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.zb{background:var(--zbar);padding:8px 10px 14px;display:flex;align-items:center;gap:8px}
.zb .in{flex:1;background:var(--zbub);color:var(--zmut);border-radius:22px;padding:9px 14px;font-size:14px}
.zb .go{width:38px;height:38px;border-radius:50%;background:#00a884;color:#fff;display:flex;align-items:center;justify-content:center}
.modal{position:absolute;inset:0;background:rgba(0,0,0,.55);display:none;flex-direction:column;z-index:5}
.modal.on{display:flex}
.modal .box{margin:auto 0 0;background:var(--card);color:var(--tx);height:88%;border-radius:18px 18px 0 0;display:flex;flex-direction:column;overflow:hidden}
.modal header{display:flex;align-items:center;gap:8px;padding:10px 12px;border-bottom:1px solid var(--bd);font-size:13px}
.modal header b{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.modal header a,.modal header button{font:inherit;font-size:13px;border:1px solid var(--bd);background:var(--card);color:var(--tx);border-radius:999px;padding:5px 10px;cursor:pointer;text-decoration:none}
.modal iframe{flex:1;border:0;width:100%;background:#fff}
"""

JS_ZAP = """
var MSGS=%(msgs)s;var HORA=%(hora)s;
function formata(t){
  t=t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  t=t.replace(/(https?:\\/\\/[^\\s<]+)/g,function(u){return '<a class="url" href="'+(window.LINKS&&window.LINKS[u]||u)+'" target="_blank">'+u+'</a>';});
  t=t.replace(/\\*([^*\\n]+)\\*/g,'<b>$1</b>').replace(/(^|[\\s(])_([^_\\n]+)_(?=[\\s).,]|$)/g,'$1<i>$2</i>');
  return t.replace(/\\n/g,'<br>');
}
var chat=document.getElementById('chat');
function rola(b){if(b&&b.offsetHeight>chat.clientHeight-30){chat.scrollTop=b.offsetTop-10;}else{chat.scrollTop=chat.scrollHeight;}}
function tocar(){
  chat.innerHTML='<div class="zdata">'+%(data)s+'</div>';var i=0;
  (function prox(){
    if(i>=MSGS.length)return;var m=MSGS[i++];
    var d=document.createElement('div');d.className='ztype';d.innerHTML='<i></i><i></i><i></i>';chat.appendChild(d);rola();
    setTimeout(function(){
      d.remove();var b=document.createElement('div');b.className='zmsg';var h='';
      if(m.doc){h+='<button class="zdoc" onclick="abrirDoc()"><span class="pdf">PDF</span><span><div class="n">'+m.doc.nome+'</div><div class="m">'+m.doc.meta+'</div></span></button>';}
      if(m.link){h+='<a class="zlink" href="'+m.link.href+'" target="_blank"><div class="th">&#9638;</div><div class="tx"><div class="t">'+m.link.titulo+'</div><div class="h">'+m.link.host+'</div></div></a>';}
      h+=formata(m.texto)+'<div class="hr">'+HORA+' &#10003;&#10003;</div>';b.innerHTML=h;chat.appendChild(b);rola(b);setTimeout(prox,700);
    },1100);
  })();
}
function abrirDoc(){var m=document.getElementById('modal');if(!window.DOC)return;document.getElementById('docframe').src=DOC.href;document.getElementById('docnome').textContent=DOC.nome;document.getElementById('docabrir').href=DOC.href;m.classList.add('on');}
function fechaDoc(){document.getElementById('modal').classList.remove('on');}
tocar();
"""

def pagina_whatsapp(titulo, h1, eyebrow, descricao, chips, mensagens, hora, data_label, contato, voltar, doc=None, links=None):
    """mensagens: lista de dicts {texto, doc?, link?}; doc: {nome, meta, href}; links: {url_visivel: href_local}"""
    miolo = """<div class="fone"><div class="tela">
<div class="zh"><div class="av">%(ini)s</div><div><div class="nm">%(nome)s</div><div class="st">online</div></div></div>
<div class="zc" id="chat"></div>
<div class="zb"><div class="in">Mensagem</div><div class="go">&#10148;</div></div>
<div class="modal" id="modal"><div class="box"><header><b id="docnome"></b><a id="docabrir" target="_blank">Abrir em nova aba</a><button onclick="fechaDoc()">Fechar &#10005;</button></header><iframe id="docframe" title="Documento"></iframe></div></div>
</div></div>""" % dict(ini=esc(contato[:2].upper()), nome=esc(contato))
    js = 'window.DOC=%s;window.LINKS=%s;' % (json.dumps(doc or {}, ensure_ascii=False), json.dumps(links or {}, ensure_ascii=False))
    js += JS_ZAP % dict(msgs=json.dumps(mensagens, ensure_ascii=False).replace('</', '<\\/'), hora=json.dumps(hora), data=json.dumps(data_label))
    botao = '<button class="btn pri" onclick="tocar()">&#8635; Repetir</button>'
    return pagina(titulo, voltar, eyebrow, h1, descricao, chips, miolo, extra_css=CSS_ZAP, extra_js=js, acoes_extra=botao)

# ------------------------------------------------------------------ E-mail
CSS_MAIL = """
.mail{background:var(--card);border:1px solid var(--bd);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.mh{padding:18px 22px;border-bottom:1px solid var(--bd)}
.mh .as{font-size:20px;font-weight:600;line-height:26px;margin-bottom:12px}
.mh .lin{display:flex;gap:12px;align-items:center}
.mh .av{width:40px;height:40px;border-radius:50%;background:#303030;color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;flex:none}
:root[data-tema=dark] .mh .av{background:#e5e7eb;color:#1f2229}
.mh .de{font-size:14px;line-height:19px}.mh .de small{color:var(--mut);display:block}
.mh .dt{margin-left:auto;font-size:12px;color:var(--mut);white-space:nowrap}
.seg{display:inline-flex;border:1px solid var(--bd);border-radius:999px;overflow:hidden;background:var(--card)}
.seg button{font:inherit;font-size:13px;border:0;background:transparent;color:var(--mut);padding:7px 14px;cursor:pointer}
.seg button.on{background:var(--acc);color:var(--acc-tx)}
.corpo{background:#e9ebef;padding:18px;display:flex;justify-content:center}
:root[data-tema=dark] .corpo{background:#0c0e12}
.corpo iframe{border:0;background:#fff;width:100%;max-width:700px;border-radius:8px;min-height:520px;transition:max-width .25s}
.corpo.cel iframe{max-width:390px}
"""

JS_MAIL = """
function modo(m){document.getElementById('corpo').className='corpo'+(m==='cel'?' cel':'');
 document.getElementById('bd').className=m==='pc'?'on':'';document.getElementById('bc').className=m==='cel'?'on':'';setTimeout(ajusta,320);}
function ajusta(){var f=document.getElementById('mailframe');try{var d=f.contentDocument;f.style.height=(d.documentElement.scrollHeight+4)+'px';}catch(e){f.style.height='900px';}}
document.getElementById('mailframe').addEventListener('load',function(){ajusta();setTimeout(ajusta,400);});
window.addEventListener('resize',function(){setTimeout(ajusta,100)});
"""

def doc_email(fragmento, fundo='#ffffff', titulo='E-mail'):
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<base target="_blank"><title>%s</title></head><body style="margin:0;padding:0;background:%s;">%s</body></html>') % (esc(titulo), fundo, fragmento)

def pagina_email(titulo, h1, eyebrow, descricao, chips, assunto, remetente, remetente_email, destinatario, data_hora, html_email, voltar, fundo='#ffffff', celular=True):
    tem_dark = '@media (prefers-color-scheme: dark)' in html_email
    claro = re.sub(r'@media \(prefers-color-scheme: dark\)\{.*?\}\}', '', html_email, flags=re.S)
    escuro = html_email.replace('@media (prefers-color-scheme: dark){', '@media all{')
    srcdoc = esc(doc_email(claro if tem_dark else html_email, fundo, assunto))
    js_var = ''
    if tem_dark:
        js_var = ('var VAR_CLARO=%s;var VAR_ESCURO=%s;function aplicaTema(t){var f=document.getElementById("mailframe");var n=t==="dark"?VAR_ESCURO:VAR_CLARO;if(f.srcdoc!==n)f.srcdoc=n;}'
                  'window.aoMudarTema=aplicaTema;aplicaTema(document.documentElement.getAttribute("data-tema"));') % (
            json.dumps(doc_email(claro, fundo, assunto), ensure_ascii=False).replace('</', '<\\/'), json.dumps(doc_email(escuro, fundo, assunto), ensure_ascii=False).replace('</', '<\\/'))
    miolo = """<div class="mail"><div class="mh"><div class="as">%(as)s</div>
<div class="lin"><div class="av">%(ini)s</div><div class="de"><b>%(rem)s</b> &lt;%(reme)s&gt;<small>para %(dest)s</small></div><div class="dt">%(dt)s</div></div></div>
<div class="corpo" id="corpo"><iframe id="mailframe" title="E-mail" srcdoc="%(src)s"></iframe></div></div>""" % dict(
        **{'as': esc(assunto)}, ini=esc(remetente[:2].upper()), rem=esc(remetente), reme=esc(remetente_email), dest=esc(destinatario), dt=esc(data_hora), src=srcdoc)
    botoes = '<span class="seg"><button id="bd" class="on" onclick="modo(\'pc\')">Computador</button><button id="bc" onclick="modo(\'cel\')">Celular</button></span>'
    if not celular:
        botoes = ''
    return pagina(titulo, voltar, eyebrow, h1, descricao, chips, miolo, extra_css=CSS_MAIL, extra_js=JS_MAIL + js_var, acoes_extra=botoes)

# ------------------------------------------------------------------ Planilha (estilo Google Sheets)
def pagina_planilha(titulo, colunas, linhas, voltar, rotulo_aba='Página1', larguras=None):
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    larguras = larguras or [260, 170, 240, 130, 130]
    cab = '<th class="rn"></th>' + ''.join('<th>%s</th>' % letras[i] for i in range(len(colunas)))
    h1 = '<tr><td class="rn">1</td>' + ''.join('<td class="h">%s</td>' % esc(c) for c in colunas) + '</tr>'
    corpo = ''
    for n, l in enumerate(linhas, start=2):
        corpo += '<tr><td class="rn">%d</td>' % n + ''.join('<td%s>%s</td>' % (' class="num"' if isinstance(v, int) else '', esc(v)) for v in l) + '</tr>'
    cols = ''.join('<col style="width:%dpx">' % w for w in larguras[:len(colunas)])
    return """<!doctype html><html lang="pt-BR" data-tema="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%(t)s</title>
<style>
:root{--bg:#f9fbfd;--bd:#dadce0;--tx:#202124;--mut:#5f6368;--hd:#f8f9fa;--sel:#e8f0fe}
:root[data-tema=dark]{--bg:#202124;--bd:#3c4043;--tx:#e8eaed;--mut:#9aa0a6;--hd:#292a2d;--sel:#28344a}
body{margin:0;background:var(--bg);color:var(--tx);font-family:Arial,Helvetica,sans-serif;height:100vh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:12px;padding:10px 16px}
.ico{width:34px;height:42px;background:#188038;border-radius:4px;color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px}
.top .t{font-size:18px}.top small{display:block;color:var(--mut);font-size:12px}
.top .sp{flex:1}.top a.v{font-size:13px;color:var(--mut);text-decoration:none;border:1px solid var(--bd);padding:7px 12px;border-radius:999px}
.top .comp{background:#c2e7ff;color:#001d35;font-size:14px;padding:9px 18px;border-radius:999px}
.menu{display:flex;gap:18px;padding:0 16px 8px;font-size:13px;color:var(--mut);border-bottom:1px solid var(--bd)}
.fake{font-size:12px;color:var(--mut);padding:6px 16px;background:var(--hd);border-bottom:1px solid var(--bd)}
.area{flex:1;overflow:auto}
table{border-collapse:collapse;font-size:13px;table-layout:fixed}
th{background:var(--hd);color:var(--mut);font-weight:400;border:1px solid var(--bd);padding:4px;position:sticky;top:0}
td{border:1px solid var(--bd);padding:4px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;height:24px}
td.rn,th.rn{width:42px;background:var(--hd);color:var(--mut);text-align:center;padding:4px;position:sticky;left:0}
td.h{font-weight:700;background:var(--sel)}td.num{text-align:right}
.abas{display:flex;align-items:center;gap:6px;padding:6px 12px;border-top:1px solid var(--bd);background:var(--hd);font-size:13px}
.abas .a{background:var(--sel);color:#1a73e8;font-weight:700;padding:6px 14px;border-radius:4px}
.abas .tm{margin-left:auto}
.abas button{font:inherit;font-size:12px;border:1px solid var(--bd);background:transparent;color:var(--tx);padding:5px 10px;border-radius:999px;cursor:pointer}
</style><script>%(js)s</script></head><body>
<div class="top"><div class="ico">&#9638;</div><div><div class="t">%(t)s</div><small>Arquivo &nbsp; Editar &nbsp; Ver &nbsp; Inserir &nbsp; Formatar &nbsp; Dados</small></div><span class="sp"></span><a class="v" href="%(voltar)s">&larr; Voltar</a><span class="comp">Compartilhar</span></div>
<div class="menu"><span>Qualquer pessoa com o link pode ver</span></div>
<div class="fake">Modelo ilustrativo &middot; dados fictícios &middot; é isto que abre no botão da planilha</div>
<div class="area"><table><colgroup><col style="width:42px">%(cols)s</colgroup><thead><tr>%(cab)s</tr></thead><tbody>%(h1)s%(corpo)s</tbody></table></div>
<div class="abas"><span class="a">%(aba)s</span><span class="tm"><button onclick="alternarTema()">Claro / escuro</button></span></div></body></html>""" % dict(
        t=esc(titulo), js=JS_TEMA, voltar=voltar, cols=cols, cab=cab, h1=h1, corpo=corpo, aba=esc(rotulo_aba))


# ------------------------------------------------------------------ Índice e README da pasta agentes/modelos/
CSS_INDICE = """
.cab{max-width:1180px;margin:0 auto;padding:46px 20px 8px}
.cab h1{font-size:40px;line-height:46px;letter-spacing:-1px;margin:6px 0 10px}
.cab p{color:var(--mut);max-width:680px;line-height:26px;margin:0}
.grade{max-width:1180px;margin:0 auto;padding:26px 20px 60px;display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px}
.cartao{background:var(--card);border:1px solid var(--bd);border-radius:18px;padding:24px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:14px}
.cartao .ic{font-size:32px}.cartao h2{margin:0;font-size:22px;letter-spacing:-.4px}
.cartao .rs{color:var(--mut);line-height:22px;font-size:14px;margin:0}
.meta{display:flex;flex-direction:column;gap:6px;font-size:13px}
.meta span b{display:inline-block;min-width:96px;font-size:11px;letter-spacing:.9px;text-transform:uppercase;color:var(--mut)}
.pecas{display:flex;flex-direction:column;gap:8px;margin-top:4px}
.pecas a{display:flex;gap:10px;align-items:center;text-decoration:none;border:1px solid var(--bd);border-radius:12px;padding:11px 13px;font-size:14px;background:var(--bg)}
.pecas a:hover{border-color:var(--acc);transform:translateY(-1px)}
.pecas a span.s{margin-left:auto;color:var(--mut)}
.nota{font-size:12.5px;background:var(--chip);color:var(--chip-tx);padding:8px 10px;border-radius:8px}
.rodape{max-width:1180px;margin:0 auto;padding:0 20px 40px;color:var(--mut);font-size:13px;line-height:20px}
"""

README_MODELOS = """# Modelos de comunicação dos fluxos

Modelos navegáveis do que cada fluxo envia, para **apresentação**. Abra o arquivo `index.html` no navegador.

Todos os nomes, telefones, e-mails, empresas e valores são **fictícios**. O layout, os textos e a ordem das informações
seguem o que os fluxos enviam de verdade.

Cada pasta tem o nome do agente e guarda as peças dele: WhatsApp do vendedor ou cliente, e-mail, documento, consolidado
do gestor e planilhas. O padrão está em `.claude/waipe/modelos-comunicacao/PADRAO.md`.

Os arquivos são estáticos e não se atualizam sozinhos: se o texto ou o layout mudar no fluxo, refaça os modelos dele.
"""

def card(nome, icone, frequencia, quem, resumo, pasta, pecas, nota=''):
    """pecas: lista de (emoji, rótulo, caminho relativo à pasta do agente). Devolve o HTML do cartão do índice."""
    links = ''.join('<a href="%s/%s"><span>%s</span>%s<span class="s">&rarr;</span></a>' % (pasta, arq, ic, esc(rot)) for ic, rot, arq in pecas)
    aviso = '<div class="nota">%s</div>' % esc(nota) if nota else ''
    return ('<!--cartao:%(p)s--><div class="cartao"><div class="ic">%(ic)s</div><h2>%(n)s</h2><p class="rs">%(rs)s</p>'
            '<div class="meta"><span><b>Frequência</b>%(f)s</span><span><b>Quem recebe</b>%(q)s</span></div>%(av)s<div class="pecas">%(l)s</div></div><!--/cartao:%(p)s-->') % dict(
        p=pasta, ic=icone, n=esc(nome), rs=esc(resumo), f=esc(frequencia), q=esc(quem), av=aviso, l=links)

def indice_novo(cartoes_html):
    return ('<!doctype html><html lang="pt-BR" data-tema="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Modelos de comunicação · Fluxos Waipe</title><style>' + CSS_BASE + CSS_INDICE + '</style><script>' + JS_TEMA + '</script></head><body>'
            '<div class="topo"><span class="marca">waipe</span><span class="espaco"></span><button class="btn" onclick="alternarTema()">Claro / escuro</button></div>'
            '<div class="cab"><div class="eyebrow">Fluxos de comunicação</div><h1>O que cada fluxo envia</h1>'
            '<p>Modelos navegáveis das mensagens, e-mails, documentos e planilhas que os fluxos enviam. Abra cada peça para ver exatamente como chega.</p></div>'
            '<div class="grade"><!--CARDS-->' + cartoes_html + '<!--/CARDS--></div>'
            '<div class="rodape">Todos os nomes, telefones, e-mails, empresas e valores destes modelos são fictícios. O layout, os textos e a ordem das informações seguem o que os fluxos enviam de verdade.</div>'
            '</body></html>')

def atualizar_indice(pasta_modelos, cartao_html, pasta_agente):
    """Cria agentes/modelos/index.html se não existir; se existir, só ADICIONA o cartão do fluxo novo
    (ou troca o cartão do mesmo agente). Nunca recria nem mexe nos cartões dos outros fluxos."""
    import os
    os.makedirs(pasta_modelos, exist_ok=True)
    caminho = os.path.join(pasta_modelos, 'index.html')
    if not os.path.exists(caminho):
        open(caminho, 'w', encoding='utf-8').write(indice_novo(cartao_html))
    else:
        h = open(caminho, encoding='utf-8').read()
        if '<!--CARDS-->' not in h:  # índice antigo, sem marcadores: marca a grade sem alterar os cartões existentes
            h = h.replace('<div class="grade">', '<div class="grade"><!--CARDS-->', 1)
            h = re.sub(r'</div>(\s*<div class="rodape">)', r'<!--/CARDS--></div>\1', h, count=1)
        marca_ini, marca_fim = '<!--cartao:%s-->' % pasta_agente, '<!--/cartao:%s-->' % pasta_agente
        if marca_ini in h:
            h = re.sub(re.escape(marca_ini) + '.*?' + re.escape(marca_fim), lambda m: cartao_html, h, flags=re.S)
        else:
            h = h.replace('<!--/CARDS-->', cartao_html + '<!--/CARDS-->', 1)
        open(caminho, 'w', encoding='utf-8').write(h)
    leia = os.path.join(pasta_modelos, 'README.md')
    if not os.path.exists(leia):
        open(leia, 'w', encoding='utf-8').write(README_MODELOS)
