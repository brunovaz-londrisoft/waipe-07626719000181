#!/usr/bin/env python3
"""waipe — ferramenta do framework de agentes Waipe.

Uso: python3 .claude/waipe/waipe.py <comando> [argumentos]

Comandos do repositório de cliente (branch única: main)
  status                       versão do framework e situação de cada agente
  validar [pasta ...]          valida agentes (padrão: agentes/ e o catálogo)
  novo-agente <slug>           cria agentes/<slug>/ com o .md do modelo
  salvar                       valida e envia para a main o que já foi commitado
  release <slug> <nivel>       fecha a versão do agente (patch|minor|major|X.Y.Z): tag <slug>/vX.Y.Z
                               e GitHub Release com os arquivos da pasta
  atualizar [vX.Y.Z]           atualiza o framework a partir do template (não toca em agentes/)
  migrar                       uma vez: apaga develop e deixa só a main (vindo do gitflow antigo)
  iniciar "<Nome do cliente>"  prepara um repositório recém-criado do template

Comandos do repositório template (o próprio framework)
  release-framework <nivel>    fecha uma versão do framework: VERSION, CHANGELOG, tag vX.Y.Z
  novo-cliente <repo> "<Nome>" cria o repositório de um cliente a partir do template
  clientes                     lista os repositórios de cliente (tópico waipe-cliente)

Só usa a biblioteca padrão do Python, git e gh.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

TEMPLATE = os.environ.get("WAIPE_TEMPLATE", "brunovaz-londrisoft/waipe-agentes-template")
TOPICO = "waipe-cliente"
RAIZ = Path(__file__).resolve().parents[2]
WAIPE = RAIZ / ".claude" / "waipe"
AGENTES = RAIZ / "agentes"
CATALOGO = WAIPE / "catalogo"

# Tudo que pertence ao framework. A atualização apaga e recopia exatamente isto.
# O resto (agentes/, CLAUDE.md, README.md, settings.local.json) é do cliente e nunca é tocado.
FRAMEWORK = [
    ".claude/waipe",
    ".claude/settings.json",
    ".claude/rules/waipe-*",
    ".claude/skills/waipe-*",
    ".claude/agents/waipe-*",
    ".github/workflows/waipe-*",
]

TIPOS = {
    "trigger_manual", "trigger_schedule", "trigger_webhook", "trigger_zapi",
    "webhook_respond", "edit_fields", "filter", "if", "switch", "loop",
    "split_out", "merge_out", "code", "http_request", "waipe_ai", "waipe_data",
    "gmail_send", "google_sheets", "google_drive", "google_docs", "zapi_send",
}
GATILHO_PARA_TRIGGERTYPE = {
    "trigger_manual": "manual", "trigger_schedule": "schedule",
    "trigger_webhook": "webhook", "trigger_zapi": "webhook",
}
BLOCKLIST = ("constructor __proto__ prototype import require eval fetch XMLHttpRequest WebSocket "
             "localStorage sessionStorage document window globalThis self top parent Function "
             "setTimeout setInterval").split()
SECOES_AGENTE = ["## Objetivo", "## Como funciona", "## Configuração após importar", "## Como testar", "## Histórico"]
SECOES_MODELO = SECOES_AGENTE + ["## Quando usar", "## Perguntas para personalizar"]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Pastas de agentes/ que não são agentes: `agentes/modelos/` guarda os modelos de comunicação (ver .claude/waipe/modelos/PADRAO.md).
RESERVADAS = {"modelos"}
CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


# ---------------------------------------------------------------- utilidades

def erro(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def run(*cmd, capturar=True, checar=True, cwd=RAIZ):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capturar)
    if checar and r.returncode != 0:
        detalhe = (r.stderr or r.stdout or "").strip() if capturar else ""
        erro(f"falhou: {' '.join(cmd)}\n{detalhe}")
    return (r.stdout or "").strip() if capturar else ""


def git(*args, **kw):
    return run("git", *args, **kw)


def gh(*args, **kw):
    return run("gh", *args, **kw)


def modo_template():
    url = git("remote", "get-url", "origin", checar=False)
    return url.rstrip("/").removesuffix(".git").endswith(TEMPLATE)


def versao_framework(raiz=RAIZ):
    return (raiz / ".claude" / "waipe" / "VERSION").read_text(encoding="utf-8").strip()


def exigir_limpo():
    if git("status", "--porcelain"):
        erro("há alterações não commitadas. Faça commit (ou descarte) antes.")


def ramo_atual():
    return git("rev-parse", "--abbrev-ref", "HEAD")


def existe_remoto(ref):
    return git("rev-parse", "--verify", "--quiet", ref, checar=False) != ""


def tag_remota_existe(tag):
    return git("ls-remote", "--tags", "origin", f"refs/tags/{tag}", checar=False) != ""


def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto.replace("\r\n", "\n"), re.S)
    if not m:
        return None
    dados = {}
    for linha in m.group(1).splitlines():
        if ":" in linha:
            k, v = linha.split(":", 1)
            dados[k.strip()] = v.strip().strip('"')
    return dados


def secao_historico(texto, versao):
    """Devolve o bloco '### vX.Y.Z' do histórico do .md (para notas de PR e release)."""
    m = re.search(rf"^(#{{2,3}}) v{re.escape(versao)}\b.*?(?=^\1 |\Z)", texto, re.S | re.M)
    return m.group(0).strip() if m else f"v{versao}"


# ---------------------------------------------------------------- validação

def _strings(obj, chave=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v, chave)
    elif isinstance(obj, str):
        yield chave, obj


def _credenciais(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "credentialId" and isinstance(v, str) and v not in ("", "CREDENTIAL_REDACTED"):
                yield v
            yield from _credenciais(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _credenciais(v)


def validar_flow(caminho):
    """Regras da Parte 2.5 e do checklist da Parte 6 do guia dos nodes. Devolve (erros, avisos)."""
    erros, avisos = [], []
    try:
        flow = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"], []
    if not isinstance(flow, dict) or not isinstance(flow.get("nodes"), list) or not isinstance(flow.get("edges"), list):
        return ["a raiz precisa ser um objeto com 'nodes' e 'edges' como arrays"], []

    versao = flow.get("waipe_flow_version")
    if versao not in (None, "1", "2"):
        erros.append(f"waipe_flow_version '{versao}' inválido (use \"2\")")
    elif versao != "2":
        avisos.append('use waipe_flow_version: "2"')
    if len(str(flow.get("name", ""))) > 200:
        erros.append("name do flow passa de 200 caracteres")

    nodes, ids, nomes, gatilhos = {}, set(), set(), []
    for i, n in enumerate(flow["nodes"]):
        nid = n.get("id") if isinstance(n, dict) else None
        if not isinstance(nid, str) or not nid:
            erros.append(f"node #{i} sem id")
            continue
        if nid in ids:
            erros.append(f"id de node repetido: {nid}")
        ids.add(nid)
        nodes[nid] = n
        tipo = n.get("type")
        if tipo not in TIPOS:
            erros.append(f"node {nid}: type '{tipo}' não existe no Waipe Flow")
        if tipo and str(tipo).startswith("trigger_"):
            gatilhos.append(n)
        nome = n.get("name", nid)
        if nome in nomes:
            erros.append(f"nome de node repetido: '{nome}' (quebra $node[\"{nome}\"])")
        nomes.add(nome)
        pos = n.get("position") or {}
        if not all(isinstance(pos.get(k), (int, float)) for k in ("x", "y")):
            erros.append(f"node {nid}: position.x/position.y precisam ser números")
        if "parameters" in n and not isinstance(n["parameters"], dict):
            erros.append(f"node {nid}: parameters precisa ser objeto")

    if len(gatilhos) != 1:
        erros.append(f"o flow precisa de exatamente 1 gatilho (tem {len(gatilhos)})")
    else:
        esperado = GATILHO_PARA_TRIGGERTYPE.get(gatilhos[0].get("type"))
        tt = flow.get("triggerType")
        if tt is None:
            avisos.append(f'defina triggerType: "{esperado}" na raiz')
        elif tt != esperado:
            erros.append(f"triggerType '{tt}' não combina com o gatilho {gatilhos[0].get('type')} (use '{esperado}')")

    saidas, filhos, grau = {}, {nid: [] for nid in nodes}, {nid: 0 for nid in nodes}
    for i, e in enumerate(flow["edges"]):
        if not isinstance(e, dict) or not all(isinstance(e.get(k), str) and e.get(k) for k in ("id", "source", "target")):
            erros.append(f"edge #{i}: precisa de id, source e target")
            continue
        s, t = e["source"], e["target"]
        if s not in nodes or t not in nodes:
            erros.append(f"edge {e['id']}: source/target apontam para node inexistente")
            continue
        if "targetHandle" in e:
            erros.append(f"edge {e['id']}: remova targetHandle")
        tipo, params = nodes[s].get("type"), nodes[s].get("parameters") or {}
        handle = e.get("sourceHandle")
        if tipo == "if":
            validos = {"true", "false"}
        elif tipo == "loop":
            validos = {"loop", "done"}
        elif tipo == "switch":
            validos = {r.get("outputLabel") for r in params.get("rules", []) if r.get("outputLabel")}
            if params.get("fallbackEnabled"):
                validos.add(params.get("fallbackLabel", "Outros"))
        else:
            validos = None
        if validos is None:
            if handle is not None:
                erros.append(f"edge {e['id']}: node {tipo} não usa sourceHandle")
        else:
            if handle not in validos:
                erros.append(f"edge {e['id']}: sourceHandle '{handle}' inválido para {tipo} (use {sorted(validos)})")
            chave = (s, handle)
            if chave in saidas:
                erros.append(f"node {s}: duas edges saindo do handle '{handle}'")
            saidas[chave] = True
        filhos[s].append(t)
        grau[t] += 1

    fila = [n for n, g in grau.items() if g == 0]
    visitados = 0
    while fila:
        n = fila.pop()
        visitados += 1
        for f in filhos[n]:
            grau[f] -= 1
            if grau[f] == 0:
                fila.append(f)
    if visitados != len(nodes):
        erros.append("o grafo tem ciclo (o Waipe Flow exige DAG; use loop ou code)")
    alvos = {t for fs in filhos.values() for t in fs}
    for nid, n in nodes.items():
        if nid not in alvos and not str(n.get("type", "")).startswith("trigger_"):
            avisos.append(f"node {nid} ('{n.get('name', nid)}') não tem conexão de entrada e nunca executa")

    for nid, n in nodes.items():
        for chave, valor in _strings(n.get("parameters") or {}):
            if chave == "jsCode" or "{{" not in valor:
                continue
            for token in BLOCKLIST:
                if re.search(rf"\b{re.escape(token)}\b", valor):
                    erros.append(f"node {nid}: expressão com token proibido '{token}' ({chave})")
                elif re.search(rf"\b{re.escape(token)}", valor):
                    avisos.append(f"node {nid}: campo começando com '{token}' em expressão ({chave}), pode ser barrado")
        params = n.get("parameters") or {}
        for k, v in params.items():
            if isinstance(v, str) and "{{" in v and params.get(f"{k}Mode") == "fixed":
                avisos.append(f"node {nid}: '{k}' tem {{{{ }}}} mas {k}Mode é 'fixed'")
    for cred in _credenciais(flow):
        erros.append(f"credentialId preenchido ('{cred}'): deixe \"\" e conecte a credencial no painel")
    return erros, avisos


def validar_pasta(pasta, exigir_par=True, modelo=False):
    pasta = Path(pasta)
    slug = pasta.name
    erros, avisos = [], []
    js, md = pasta / f"{slug}.json", pasta / f"{slug}.md"
    if not SLUG.match(slug):
        erros.append(f"nome da pasta '{slug}' deve ser kebab-case (ex.: clientes-inativos)")
    if js.exists():
        e, a = validar_flow(js)
        erros += e
        avisos += a
    elif exigir_par:
        erros.append(f"falta {js.name}")
    if md.exists():
        texto = md.read_text(encoding="utf-8")
        fm = frontmatter(texto)
        if fm is None:
            erros.append(f"{md.name}: falta o cabeçalho --- (nome, slug, versao)")
        else:
            if fm.get("nome", "").startswith("Nome legível"):
                erros.append(f"{md.name}: preencha o campo nome do cabeçalho")
            if fm.get("slug") != slug:
                erros.append(f"{md.name}: slug '{fm.get('slug')}' difere da pasta '{slug}'")
            if not SEMVER.match(fm.get("versao", "")):
                erros.append(f"{md.name}: versao '{fm.get('versao')}' não é X.Y.Z")
            elif fm["versao"] != "0.0.0" and f"### v{fm['versao']}" not in texto:
                erros.append(f"{md.name}: o Histórico não tem a entrada '### v{fm['versao']}'")
        if js.exists() and "Data Lab" not in texto:
            try:
                nodes = json.loads(js.read_text(encoding="utf-8")).get("nodes", [])
            except ValueError:
                nodes = []
            if any(n.get("type") == "waipe_data" and (n.get("parameters") or {}).get("dataSource") == "data_lab" for n in nodes):
                avisos.append(f"{md.name}: o flow usa Data Lab, documente o texto (prompt) de cada relatório (seção 'Relatórios do Data Lab')")
        for s in (SECOES_MODELO if modelo else SECOES_AGENTE):
            if not re.search(rf"^{re.escape(s)}\b", texto, re.M):
                erros.append(f"{md.name}: falta a seção '{s}'")
    elif exigir_par:
        erros.append(f"falta {md.name}")
    if modelo:
        for arq in (js, md):
            if arq.exists():
                conteudo = arq.read_text(encoding="utf-8")
                if CNPJ.search(conteudo):
                    erros.append(f"{arq.name}: tem CNPJ, modelo do catálogo deve ser anônimo")
                for em in EMAIL.findall(conteudo):
                    if not em.endswith(("exemplo.com", "example.com", "exemplo.com.br")):
                        erros.append(f"{arq.name}: tem e-mail real ({em}), use algo@exemplo.com")
    return erros, avisos


def pastas_agentes():
    return sorted(p for p in AGENTES.iterdir() if p.is_dir() and p.name not in RESERVADAS) if AGENTES.exists() else []


def pastas_padrao():
    pastas = pastas_agentes()
    if CATALOGO.exists():
        pastas += sorted(p for p in CATALOGO.iterdir() if p.is_dir())
    return pastas


def cmd_validar(args):
    pastas = [Path(a).resolve() for a in args] or pastas_padrao()
    falhou = False
    for p in pastas:
        e, a = validar_pasta(p, modelo=CATALOGO in p.parents)
        rel = p.relative_to(RAIZ) if RAIZ in p.parents else p
        print(f"{'✗' if e else '✓'} {rel}")
        for x in e:
            print(f"    erro:  {x}")
        for x in a:
            print(f"    aviso: {x}")
        falhou |= bool(e)
    if not pastas:
        print("nenhum agente para validar")
    sys.exit(1 if falhou else 0)


def cmd_hook(_args):
    """PostToolUse do Claude Code: valida a pasta do agente que acabou de ser editada."""
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    caminho = Path((evento.get("tool_input") or {}).get("file_path", "")).resolve()
    if caminho.suffix not in (".json", ".md"):
        return
    for base in (AGENTES, CATALOGO):
        if base in caminho.parents and caminho.parent.parent == base and caminho.parent.name not in RESERVADAS:
            erros, _ = validar_pasta(caminho.parent, exigir_par=False, modelo=base == CATALOGO)
            if erros:
                print(f"Validação de {caminho.parent.name} falhou:\n- " + "\n- ".join(erros), file=sys.stderr)
                sys.exit(2)


# ---------------------------------------------------------------- fluxo do cliente (branch única: main)

NAO_PUBLICADO = "### Não publicado"
NIVEIS = ("patch", "minor", "major")


def ultima_tag(prefixo):
    tags = git("tag", "-l", f"{prefixo}v*", "--sort=-v:refname").splitlines()
    return tags[0] if tags else ""


def mudou_desde(tag, caminho):
    if not tag:
        return True
    return bool(git("diff", "--name-only", tag, "HEAD", "--", caminho))


def proxima_versao(atual, pedido):
    if SEMVER.match(pedido):
        return pedido
    if pedido not in NIVEIS:
        erro(f"versão '{pedido}' inválida: use patch, minor, major ou X.Y.Z")
    ma, mi, pa = (int(x) for x in atual.split("."))
    return {"patch": f"{ma}.{mi}.{pa + 1}", "minor": f"{ma}.{mi + 1}.0", "major": f"{ma + 1}.0.0"}[pedido]


def exigir_main():
    if ramo_atual() != "main":
        erro(f"você está em '{ramo_atual()}'. Este repositório trabalha só na main (rode 'migrar' se ainda tiver develop).")


def puxar_main():
    git("fetch", "origin", "--tags")
    git("pull", "--rebase", "-q", "origin", "main")


def envia_mensagens(pasta):
    """True se o flow do agente envia e-mail, WhatsApp (zapi_send ou Z-API por http_request) ou cria documento/planilha."""
    js = pasta / f"{pasta.name}.json"
    if not js.exists():
        return False
    try:
        nodes = json.loads(js.read_text(encoding="utf-8")).get("nodes", [])
    except ValueError:
        return False
    for n in nodes:
        t = n.get("type")
        if t in ("gmail_send", "zapi_send"):
            return True
        if t == "http_request" and "z-api" in str((n.get("parameters") or {}).get("url", "")).lower():
            return True
    return False


def situacao_modelos(pasta):
    """Sufixo da linha do status: modelos de comunicação do agente em agentes/modelos/<slug>/."""
    if modo_template() or not envia_mensagens(pasta):
        return ""
    return "  modelos: ok" if (AGENTES / "modelos" / pasta.name).is_dir() else "  modelos: PENDENTE"


def cmd_status(_args):
    git("fetch", "-q", "origin", "--tags", checar=False)
    print(f"Framework: v{versao_framework()}  ({'template' if modo_template() else 'cliente'})")
    print(f"Branch:    {ramo_atual()}")
    pendentes = git("log", "origin/main..HEAD", "--oneline", checar=False)
    if pendentes:
        print(f"Commits ainda não enviados: {len(pendentes.splitlines())} (rode 'salvar')")
    pastas = pastas_agentes()
    if not pastas:
        print("Agentes:   nenhum")
    for p in pastas:
        tag = ultima_tag(f"{p.name}/")
        publicada = tag.split("/v")[1] if tag else "nunca"
        alterado = "com alterações desde a última release" if mudou_desde(tag, f"agentes/{p.name}") else "sem alterações"
        print(f"  {p.name:<32} última release: {publicada:<8} {alterado}{situacao_modelos(p)}")
    if CATALOGO.exists():
        modelos = [p.name for p in sorted(CATALOGO.iterdir()) if p.is_dir()]
        print(f"Catálogo:  {', '.join(modelos) or 'vazio'}")


def cmd_novo_agente(args):
    if len(args) != 1 or not SLUG.match(args[0]):
        erro("uso: novo-agente <slug-em-kebab-case>")
    if modo_template():
        erro("no template não há agentes; o trabalho é no framework.")
    slug = args[0]
    if slug in RESERVADAS:
        erro(f"'{slug}' é nome reservado (agentes/{slug}/ não é um agente).")
    pasta = AGENTES / slug
    if pasta.exists():
        erro(f"{pasta.relative_to(RAIZ)}/ já existe: é só alterar os arquivos.")
    pasta.mkdir(parents=True)
    modelo = (WAIPE / "modelo-agente.md").read_text(encoding="utf-8")
    hoje = datetime.date.today().isoformat()
    (pasta / f"{slug}.md").write_text(modelo.replace("{{slug}}", slug).replace("{{data}}", hoje), encoding="utf-8")
    print(f"Novo agente: {pasta.relative_to(RAIZ)}/ (preencha {slug}.md e crie {slug}.json)")


def cmd_salvar(_args):
    """Valida e envia para a main o que já foi commitado. O usuário testa a partir da main."""
    exigir_main()
    exigir_limpo()
    erros = [f"{p.name}: {x}" for p in pastas_padrao() for x in validar_pasta(p, modelo=CATALOGO in p.parents)[0]]
    if erros:
        erro("não passou na validação:\n- " + "\n- ".join(erros))
    puxar_main()
    if not git("log", "origin/main..HEAD", "--oneline"):
        print("Nada novo para enviar: a main local já está igual ao GitHub.")
        return
    enviados = git("log", "origin/main..HEAD", "--format=- %s")
    git("push", "origin", "main")
    print(f"Enviado para a main:\n{enviados}")


def cmd_release(args):
    """Fecha a release de um agente: versão no .md, histórico, tag <slug>/vX.Y.Z e GitHub Release com a pasta."""
    if len(args) != 2:
        erro("uso: release <slug> <patch|minor|major|X.Y.Z>")
    slug, pedido = args
    if slug in RESERVADAS:
        erro(f"'{slug}' não é um agente (pasta reservada).")
    exigir_main()
    exigir_limpo()
    pasta = AGENTES / slug
    md = pasta / f"{slug}.md"
    if not md.exists():
        erro(f"{md.relative_to(RAIZ)} não existe.")
    puxar_main()
    anterior = ultima_tag(f"{slug}/")
    if anterior and not mudou_desde(anterior, f"agentes/{slug}"):
        erro(f"nada mudou em agentes/{slug}/ desde {anterior}.")
    texto = md.read_text(encoding="utf-8")
    fm = frontmatter(texto) or {}
    base = anterior.split("/v")[1] if anterior else fm.get("versao", "0.0.0")
    # Primeira release de um agente novo (0.0.0) sai como 1.0.0, a não ser que o usuário dê a versão exata.
    versao = "1.0.0" if base == "0.0.0" and pedido in NIVEIS else proxima_versao(base, pedido)
    tag = f"{slug}/v{versao}"
    if tag_remota_existe(tag):
        erro(f"a tag {tag} já existe.")
    hoje = datetime.date.today().isoformat()
    cabecalho = f"### v{versao} ({hoje})"
    if NAO_PUBLICADO in texto:
        texto = texto.replace(NAO_PUBLICADO, cabecalho, 1)
    elif f"### v{versao}" not in texto:
        texto = re.sub(r"^## Histórico\n\n", f"## Histórico\n\n{cabecalho}\n- Release sem notas.\n\n", texto, count=1, flags=re.M)
    texto = re.sub(r"^versao: .*$", f"versao: {versao}", texto, count=1, flags=re.M)
    texto = re.sub(r"^atualizado: .*$", f"atualizado: {hoje}", texto, count=1, flags=re.M)
    md.write_text(texto, encoding="utf-8")
    erros, _ = validar_pasta(pasta)
    if erros:
        git("checkout", "--", str(md))
        erro("o agente não passou na validação:\n- " + "\n- ".join(erros))
    git("add", str(md))
    git("commit", "-q", "-m", f"release({slug}): v{versao}")
    git("push", "origin", "main")
    nome = fm.get("nome", slug)
    git("tag", "-a", tag, "-m", f"{nome} v{versao}")
    git("push", "origin", tag)
    notas = secao_historico(texto, versao)
    arquivos = [str(a.relative_to(RAIZ)) for a in sorted(pasta.iterdir()) if a.is_file()]
    url = gh("release", "create", tag, *arquivos, "--title", f"{nome} v{versao}", "--notes", notas, "--verify-tag")
    print(f"Release fechada: {tag}\n{url}\nAnexos: {', '.join(Path(a).name for a in arquivos)}")


def cmd_migrar(_args):
    """Uma vez por repositório: sai do gitflow antigo (develop/feature) para a branch única main."""
    exigir_limpo()
    git("fetch", "origin", "--prune")
    if existe_remoto("origin/develop"):
        # Compara o conteúdo, não os commits: o release antigo copiava a pasta do agente para a main.
        fora = git("diff", "--stat", "origin/main", "origin/develop")
        if fora:
            erro("develop tem conteúdo que não está na main. Leve-o para a main antes de migrar:\n" + fora)
    git("switch", "main")
    git("pull", "--ff-only", "-q", "origin", "main")
    if existe_remoto("origin/develop"):
        git("push", "origin", "--delete", "develop")
    for ramo in git("branch", "--format=%(refname:short)").splitlines():
        if ramo != "main" and (ramo == "develop" or ramo.startswith(("feature/", "release/", "publicar/", "framework/"))):
            git("branch", "-d", ramo, checar=False)  # -d: nunca apaga branch com trabalho que não está na main
    sobras = [r for r in git("branch", "--format=%(refname:short)").splitlines() if r != "main"]
    if sobras:
        print("Branches locais com trabalho fora da main (não apagadas): " + ", ".join(sobras))
    print("Migrado: só a branch main. Trabalhe nela e use 'salvar' e 'release <slug> <nivel>'.")


def cmd_atualizar(args):
    if modo_template():
        erro("este é o template. Atualização é para repositórios de cliente.")
    exigir_main()
    exigir_limpo()
    alvo = args[0] if args else gh("api", f"repos/{TEMPLATE}/releases/latest", "--jq", ".tag_name")
    alvo = "v" + alvo.lstrip("v")
    atual = "v" + versao_framework()
    if alvo == atual:
        print(f"Já está na versão {atual}.")
        return
    puxar_main()
    with tempfile.TemporaryDirectory() as tmp:
        pacote = Path(tmp) / "fw.tgz"
        with open(pacote, "wb") as f:
            subprocess.run(["gh", "api", f"repos/{TEMPLATE}/tarball/{alvo}"], stdout=f, check=True)
        with tarfile.open(pacote) as tar:
            tar.extractall(tmp, filter="data")
        novo = next(p for p in Path(tmp).iterdir() if p.is_dir())
        for padrao in FRAMEWORK:
            for velho in RAIZ.glob(padrao):
                shutil.rmtree(velho) if velho.is_dir() else velho.unlink()
            for item in novo.glob(padrao):
                destino = RAIZ / item.relative_to(novo)
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(item, destino) if item.is_dir() else shutil.copy2(item, destino)
        git("add", "-A", "--", ".claude", ".github")
    if not git("status", "--porcelain"):
        print("Nada mudou nos arquivos do framework.")
        return
    alteracoes = [l for l in git("status", "--porcelain").splitlines() if not l[3:].startswith((".claude/", ".github/"))]
    if alteracoes:
        git("reset", "-q", "--hard", "HEAD")
        erro("a atualização tocou fora do framework, abortando:\n" + "\n".join(alteracoes))
    git("commit", "-q", "-m", f"chore: framework {atual} -> {alvo}")
    git("push", "origin", "main")
    print(f"Framework atualizado {atual} -> {alvo} (direto na main).")


def cmd_iniciar(args):
    if len(args) != 1:
        erro('uso: iniciar "<Nome do cliente>"')
    if modo_template():
        erro("este é o template. 'iniciar' é para repositórios de cliente.")
    nome = args[0]
    claude = RAIZ / "CLAUDE.md"
    texto = claude.read_text(encoding="utf-8")
    if "Cliente: PENDENTE" in texto:
        claude.write_text(texto.replace("Cliente: PENDENTE", f"Cliente: {nome}"), encoding="utf-8")
        (RAIZ / "README.md").write_text(
            f"# Agentes Waipe · {nome}\n\n"
            "Flows do Waipe Flow deste cliente, versionados com o framework `waipe-agentes-template`.\n\n"
            "- Cada agente fica em `agentes/<slug>/` com o `.json` (para importar) e o `.md` (documentação).\n"
            "- Uma branch só, `main`: o que está nela é a versão em trabalho, que você importa e testa.\n"
            "- Versões fechadas: aba **Releases** (tag `<slug>/vX.Y.Z`, com os arquivos do agente anexados).\n"
            "- Como trabalhar: `.claude/waipe/LEIAME.md`.\n", encoding="utf-8")
        git("add", "CLAUDE.md", "README.md")
        git("commit", "-q", "-m", f"chore: iniciar repositório de {nome}")
        git("push", "origin", "HEAD:main")
    gh("repo", "edit", "--add-topic", TOPICO)
    git("switch", "main")
    print(f"Repositório de {nome} pronto (framework v{versao_framework()}). Branch: main.")


# ---------------------------------------------------------------- template (o próprio framework)

def cmd_release_framework(args):
    """Fecha uma versão do framework: VERSION, seção do CHANGELOG, tag vX.Y.Z e GitHub Release."""
    if not modo_template():
        erro("release-framework só roda no repositório template.")
    if len(args) != 1:
        erro("uso: release-framework <patch|minor|major|X.Y.Z>")
    exigir_main()
    exigir_limpo()
    puxar_main()
    versao = proxima_versao(versao_framework(), args[0])
    tag = f"v{versao}"
    if tag_remota_existe(tag):
        erro(f"a tag {tag} já existe.")
    changelog_md = WAIPE / "CHANGELOG.md"
    changelog = changelog_md.read_text(encoding="utf-8")
    hoje = datetime.date.today().isoformat()
    if "## Não publicado" not in changelog:
        erro("escreva as mudanças em '## Não publicado' no .claude/waipe/CHANGELOG.md antes de fechar a versão.")
    changelog = changelog.replace("## Não publicado", f"## {tag} ({hoje})", 1)
    changelog_md.write_text(changelog, encoding="utf-8")
    (WAIPE / "VERSION").write_text(versao + "\n", encoding="utf-8")
    git("add", str(changelog_md), str(WAIPE / "VERSION"))
    git("commit", "-q", "-m", f"release: framework {tag}")
    git("push", "origin", "main")
    git("tag", "-a", tag, "-m", f"Framework {tag}")
    git("push", "origin", tag)
    notas = secao_historico(changelog, versao)
    gh("release", "create", tag, "--title", f"Framework {tag}", "--notes", notas, "--verify-tag")
    print(f"Framework {tag} publicado.\nAtualize os clientes com a skill waipe-atualizar-framework.")


def cmd_clientes(_args):
    dono = TEMPLATE.split("/")[0]
    print(gh("repo", "list", dono, "--topic", TOPICO, "--limit", "200",
             "--json", "nameWithOwner,updatedAt", "--jq", ".[] | \"\\(.nameWithOwner)\\t\\(.updatedAt)\""))


def cmd_novo_cliente(args):
    if len(args) != 2:
        erro('uso: novo-cliente <nome-do-repo> "<Nome do cliente>"')
    repo, nome = args
    dono = TEMPLATE.split("/")[0]
    completo = repo if "/" in repo else f"{dono}/{repo}"
    destino = RAIZ.parent / completo.split("/")[1]
    if destino.exists():
        erro(f"{destino} já existe")
    gh("repo", "create", completo, "--private", "--template", TEMPLATE)
    for _ in range(60):  # o GitHub copia o template de forma assíncrona
        pronto = subprocess.run(["gh", "api", f"repos/{completo}/contents/.claude/waipe/VERSION"],
                                capture_output=True, text=True)
        if pronto.returncode == 0:
            break
        time.sleep(2)
    else:
        erro(f"o GitHub não terminou de copiar o template para {completo}. Tente clonar mais tarde.")
    run("gh", "repo", "clone", completo, str(destino), cwd=RAIZ.parent)
    for chave in ("user.name", "user.email"):  # mesma identidade de commit do template
        valor = git("config", "--local", chave, checar=False)
        if valor:
            git("config", chave, valor, cwd=destino)
    run(sys.executable, str(destino / ".claude/waipe/waipe.py"), "iniciar", nome, cwd=destino, capturar=False)
    print(f"Cliente criado: https://github.com/{completo}  ({destino})")


COMANDOS = {
    "validar": cmd_validar, "hook": cmd_hook, "status": cmd_status, "novo-agente": cmd_novo_agente,
    "salvar": cmd_salvar, "release": cmd_release, "atualizar": cmd_atualizar, "migrar": cmd_migrar,
    "iniciar": cmd_iniciar, "release-framework": cmd_release_framework,
    "novo-cliente": cmd_novo_cliente, "clientes": cmd_clientes,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    COMANDOS[sys.argv[1]](sys.argv[2:])
