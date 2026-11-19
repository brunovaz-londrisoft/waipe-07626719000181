#!/usr/bin/env python3
"""plugins — páginas do Waipe Páginas (plugins .json) no repositório Waipe (template ou cliente waipe-<cnpj>).

Uso: python3 .claude/waipe/plugins.py <comando> [argumentos]

  status                       situação de cada plugin do cliente (última release, mudou desde então)
  validar [pasta ...]          valida plugins (padrão: plugins/ e o catálogo modelos/plugins/). Estrutura, par
                               .json + .md, exemplo e, com o waipe-paginas ao lado (ou WAIPE_PAGINAS), o motor
                               completo (fórmulas, migração, painel com o exemplo)
  catalogo [termos ...]        procura um plugin parecido (catálogo modelos/plugins/ e plugins/ do cliente)
  novo <slug> [--modelo <m>]   cria a pasta do plugin (.json, .md e exemplo.json) em branco ou a partir de outro.
                               No cliente: plugins/<slug>/. No template: modelos/plugins/<slug>/ (catálogo)
  gerar-modelos [slug ...]     gera as prévias para o simulador do portal: <pasta>/modelos/painel.html,
                               relatorio.html e modelos.json (motor do waipe-paginas com o exemplo.json)
  salvar                       valida e envia para a main o que já foi commitado (o mesmo de waipe.py salvar)
  release <slug> <nivel>       fecha a versão do plugin (patch|minor|major|X.Y.Z): versao no .json e no .md,
                               histórico, prévias, tag plugins/<slug>/vX.Y.Z e GitHub Release com os arquivos.
                               No template (catálogo): só versao, histórico e prévias; publique com
                               waipe.py release-framework
  hook                         (Claude Code) valida a pasta do plugin editado

Só usa a biblioteca padrão do Python, git, gh e node (para o motor).
"""
import datetime
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WAIPE = RAIZ / ".claude" / "waipe"
FERRAMENTA = WAIPE / "plugin"
PLUGINS = RAIZ / "plugins"
CATALOGO = RAIZ / "modelos" / "plugins"
MODELO_MD = WAIPE / "modelo-plugin.md"
TEMPLATES = ("waipe-template", "waipe-agentes-template")
PREFIXO_TAG = "plugins/"
SLUG = re.compile(r"^[a-z][a-z0-9_]{1,30}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
COR = re.compile(r"^(#[0-9a-fA-F]{3,8}|var\(--[a-z0-9-]+\))$")
CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
SECOES = ["## Quando usar", "## Objetivo", "## Relatório do Data Lab", "## Como calcula", "## Banco", "## Telas",
          "## Configurações", "## Perguntas para personalizar", "## Como instalar e testar", "## Histórico"]
NAO_PUBLICADO = "### Não publicado"
NIVEIS = ("patch", "minor", "major")


def erro(msg):
    print(f"erro: {msg}", file=sys.stderr)
    sys.exit(1)


def run(*cmd, checar=True):
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    if checar and r.returncode != 0:
        erro(f"{' '.join(cmd)}\n{r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def git(*a, **kw):
    return run("git", *a, **kw)


def gh(*a, **kw):
    return run("gh", *a, **kw)


def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    return {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)}


def secao_historico(texto, versao):
    m = re.search(rf"^### v{re.escape(versao)} .*?\n(.*?)(?=^### |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else "Sem notas."


def _dirs(base):
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []


def pastas():
    """Plugins do cliente (plugins/)."""
    return _dirs(PLUGINS)


def todas():
    """Plugins do cliente e do catálogo (modelos/plugins/)."""
    return _dirs(PLUGINS) + _dirs(CATALOGO)


def modo_template():
    url = run("git", "remote", "get-url", "origin", checar=False).rstrip("/").removesuffix(".git")
    return url.split("/")[-1] in TEMPLATES


def base_trabalho():
    """Onde nascem e fecham versão os plugins: catálogo no template, plugins/ no cliente."""
    return CATALOGO if modo_template() else PLUGINS


def achar(slug):
    for base in (PLUGINS, CATALOGO):
        if (base / slug / f"{slug}.json").exists():
            return base / slug
    return None


# ---------------------------------------------------------------- validação

def _varrer(x, caminho, erros):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "link" and isinstance(v, str) and (not v.startswith("/") or v.startswith("//")):
                erros.append(f"{caminho}.link: só links internos, começando por \"/\".")
            if k == "cor" and isinstance(v, str) and not COR.match(v):
                erros.append(f"{caminho}.cor: use #rrggbb ou var(--nome).")
            _varrer(v, f"{caminho}.{k}" if caminho else k, erros)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            _varrer(v, f"{caminho}[{i}]", erros)


def validar_pasta(pasta):
    """Validação estrutural (sem o motor): devolve (erros, avisos)."""
    erros, avisos = [], []
    slug = pasta.name
    if not SLUG.match(slug):
        erros.append("nome da pasta: a-z, 0-9 e _, começando por letra (é o slug).")
    js, md, ex = pasta / f"{slug}.json", pasta / f"{slug}.md", pasta / "exemplo.json"
    plugin = None
    if not js.exists():
        erros.append(f"falta {js.name}.")
    else:
        try:
            plugin = json.loads(js.read_text(encoding="utf-8"))
        except ValueError as e:
            erros.append(f"{js.name}: JSON inválido ({e}).")
    if plugin is not None:
        if plugin.get("formato") != "waipe-paginas/1":
            erros.append(f"{js.name}: formato deve ser \"waipe-paginas/1\".")
        if plugin.get("slug") != slug:
            erros.append(f"{js.name}: slug \"{plugin.get('slug')}\" diferente da pasta ({slug}).")
        if not SEMVER.match(str(plugin.get("versao", ""))):
            erros.append(f"{js.name}: versao X.Y.Z obrigatória (a release atualiza).")
        _varrer(plugin, "", erros)
    if not md.exists():
        erros.append(f"falta {md.name}: todo .json tem o .md par.")
    else:
        texto = md.read_text(encoding="utf-8")
        fm = frontmatter(texto)
        if not fm:
            erros.append(f"{md.name}: cabeçalho (--- nome, slug, versao, plataforma, atualizado ---) ausente.")
        else:
            for k in ("nome", "slug", "versao", "plataforma", "atualizado"):
                if not fm.get(k):
                    erros.append(f"{md.name}: cabeçalho sem {k}.")
            if fm.get("slug") and fm["slug"] != slug:
                erros.append(f"{md.name}: slug do cabeçalho diferente da pasta.")
            if fm.get("versao") and not SEMVER.match(fm["versao"]):
                erros.append(f"{md.name}: versao X.Y.Z.")
            if plugin is not None and fm.get("versao") and fm["versao"] != plugin.get("versao"):
                erros.append(f"versao do .md ({fm['versao']}) diferente da do .json ({plugin.get('versao')}).")
        for s in SECOES:
            if s not in texto:
                erros.append(f"{md.name}: falta a seção \"{s}\".")
    if md.exists() and fm:
        avisos += dependencias_md(md.name, fm, texto)
        if fm.get("url") and not fm["url"].startswith("https://"):
            avisos.append(f"{md.name}: url do cabeçalho deve começar com https:// (endereço da página em produção)")
        if fm.get("url") and "## Em produção" not in texto:
            avisos.append(f"{md.name}: página em produção (url no cabeçalho): descreva na seção '## Em produção'")
    if not ex.exists():
        erros.append("falta exemplo.json (linhas fictícias do Data Lab para validar e mostrar o plugin).")
    else:
        t = ex.read_text(encoding="utf-8")
        if CNPJ.search(t) or EMAIL.search(t):
            avisos.append("exemplo.json parece ter CNPJ ou e-mail: use só dados fictícios.")
    return erros, avisos


def dependencias_md(nome, fm, texto):
    """Cabeçalho "dependencias: agente:<slug>, plugin:<slug>" (ou "nenhuma") + seção ## Dependências."""
    avisos = []
    bruto = fm.get("dependencias", "").strip()
    if not bruto or bruto.lower() in ("nenhuma", "nenhum", "-"):
        return avisos
    for x in (s.strip() for s in bruto.split(",")):
        m = re.match(r"^(agente|plugin):([a-z0-9][a-z0-9_-]*)$", x)
        if not m:
            avisos.append(f"{nome}: dependência '{x}' fora do formato (use agente:<slug> ou plugin:<slug>)")
            continue
        bases = (RAIZ / "agentes", RAIZ / "modelos" / "agentes") if m.group(1) == "agente" else (PLUGINS, CATALOGO)
        if not any((b / m.group(2) / f"{m.group(2)}.md").exists() for b in bases):
            avisos.append(f"{nome}: dependência {x} não existe neste repositório nem no catálogo")
    if not re.search(r"^## Dependências", texto, re.M):
        avisos.append(f"{nome}: tem dependências no cabeçalho, explique na seção '## Dependências'")
    return avisos


def validar_motor(lista):
    """Roda o motor do waipe-paginas (node). Devolve {slug: {erros, ...}} ou None se o motor não estiver disponível."""
    if not lista:
        return {}
    r = subprocess.run(["node", str(FERRAMENTA / "validar.mjs"), *map(str, lista)], cwd=RAIZ, capture_output=True, text=True)
    try:
        saida = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        erro(f"validação do motor falhou:\n{r.stderr.strip() or r.stdout.strip()}")
    if "semMotor" in saida:
        print(f"aviso: {saida['semMotor']} Só a validação estrutural foi feita.")
        return None
    return saida["plugins"]


def cmd_validar(args):
    lista = [Path(a).resolve() for a in args] or todas()
    ruins = 0
    motor = validar_motor(lista) or {}
    for p in lista:
        erros, avisos = validar_pasta(p)
        m = motor.get(p.name, {})
        erros += m.get("erros", [])
        for a in avisos:
            print(f"aviso {p.name}: {a}")
        if erros:
            ruins += 1
            print(f"✗ {p.name}\n  - " + "\n  - ".join(erros))
        else:
            extra = f" (exemplo: {m['linhas']} linhas → {m['itens']} itens)" if "itens" in m else ""
            print(f"✓ {p.name}{extra}")
    if ruins:
        sys.exit(1)


def cmd_hook(_args):
    try:
        evento = json.load(sys.stdin)
    except ValueError:
        return
    caminho = Path((evento.get("tool_input") or {}).get("file_path", "")).resolve()
    if caminho.suffix not in (".json", ".md") or caminho.parent.parent not in (PLUGINS, CATALOGO):
        return
    erros, _ = validar_pasta(caminho.parent)
    erros += (validar_motor([caminho.parent]) or {}).get(caminho.parent.name, {}).get("erros", [])
    # Pasta recém-criada ainda sem o par completo: só avisa o que falta no fim.
    if erros:
        print(f"Validação de {caminho.parent.name}:\n- " + "\n- ".join(erros), file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------- dia a dia

def ultima_tag(prefixo):
    tags = git("tag", "-l", f"{prefixo}v*", "--sort=-v:refname").splitlines()
    return tags[0] if tags else ""


def mudou_desde(tag, caminho):
    # As prévias (modelos/) são geradas: não contam como mudança do plugin.
    return not tag or bool(git("diff", "--name-only", tag, "HEAD", "--", caminho, f":!{caminho}/modelos"))


def proxima(atual, pedido):
    if SEMVER.match(pedido):
        return pedido
    if pedido not in NIVEIS:
        erro("use patch, minor, major ou X.Y.Z")
    ma, mi, pa = (int(x) for x in atual.split("."))
    return {"patch": f"{ma}.{mi}.{pa + 1}", "minor": f"{ma}.{mi + 1}.0", "major": f"{ma + 1}.0.0"}[pedido]


def exigir_main_limpa():
    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        erro("este repositório trabalha só na main.")
    if git("status", "--porcelain"):
        erro("há mudanças sem commit. Faça o commit antes.")


def puxar():
    if git("remote", checar=False):
        git("fetch", "-q", "origin", "--tags", checar=False)
        if subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"], cwd=RAIZ).returncode != 0:
            git("pull", "--rebase=merges", "-q", "origin", "main", checar=False)


def cmd_status(_args):
    git("fetch", "-q", "origin", "--tags", checar=False)
    pend = git("log", "origin/main..HEAD", "--oneline", checar=False)
    if pend:
        print(f"Commits ainda não enviados: {len(pend.splitlines())} (rode 'salvar')")
    if not pastas():
        print("Nenhum plugin em plugins/ ainda.")
    for p in pastas():
        tag = ultima_tag(f"{PREFIXO_TAG}{p.name}/")
        pub = tag.split("/v")[-1] if tag else "nunca"
        mud = "com alterações desde a última release" if mudou_desde(tag, f"plugins/{p.name}") else "sem alterações"
        print(f"  {p.name:<24} última release: {pub:<8} {mud}")
    if CATALOGO.exists():
        print(f"Catálogo (modelos/plugins/): {', '.join(p.name for p in _dirs(CATALOGO)) or 'vazio'}")


def _sem(t):
    return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()


def cmd_catalogo(args):
    termos = [_sem(t) for t in args]
    achados = []
    for p in todas():
        md = p / f"{p.name}.md"
        texto = md.read_text(encoding="utf-8") if md.exists() else ""
        fm = frontmatter(texto) or {}
        alvo = _sem(texto)
        nota = sum(alvo.count(t) for t in termos) if termos else 1
        if nota:
            desc = re.search(r"^## Quando usar\n\n(.+?)\n\n", texto, re.S | re.M)
            onde = "catálogo" if p.parent == CATALOGO else "deste cliente"
            achados.append((nota, p.name, fm.get("nome", p.name), fm.get("versao", "?"), (desc.group(1) if desc else "").replace("\n", " ")[:220], onde))
    if not achados:
        print("Nenhum plugin parecido: crie do zero (python3 .claude/waipe/plugins.py novo <slug>).")
        return
    for _, slug, nome, v, desc, onde in sorted(achados, reverse=True):
        print(f"* {slug} ({nome}, v{v}, {onde})\n  {desc}\n  como base: plugins.py novo <slug-novo> --modelo {slug}")


def cmd_novo(args):
    if not args:
        erro("uso: novo <slug> [--modelo <plugin>]")
    slug, modelo = args[0], None
    if "--modelo" in args:
        modelo = args[args.index("--modelo") + 1]
    if not SLUG.match(slug):
        erro("slug: a-z, 0-9 e _, começando por letra.")
    destino = base_trabalho() / slug
    if destino.exists() or achar(slug):
        erro(f"o plugin {slug} já existe.")
    origem = achar(modelo) if modelo else None
    if modelo and not origem:
        erro(f"plugin modelo '{modelo}' não existe (nem em plugins/ nem em modelos/plugins/).")
    destino.mkdir(parents=True)
    hoje = datetime.date.today().isoformat()
    if modelo:
        js = (origem / f"{modelo}.json").read_text(encoding="utf-8")
        js = re.sub(r'"slug": "[^"]*"', f'"slug": "{slug}"', js, count=1)
        js = re.sub(r'"versao": "[^"]*"', '"versao": "0.0.0"', js, count=1)
        js = js.replace(f"/{modelo}/", f"/{slug}/").replace(f"/{modelo}?", f"/{slug}?").replace(f'"/{modelo}"', f'"/{slug}"')
        (destino / f"{slug}.json").write_text(js, encoding="utf-8")
        md = (origem / f"{modelo}.md").read_text(encoding="utf-8")
        md = re.sub(r"^slug: .*$", f"slug: {slug}", md, count=1, flags=re.M)
        md = re.sub(r"^versao: .*$", "versao: 0.0.0", md, count=1, flags=re.M)
        md = re.sub(r"^atualizado: .*$", f"atualizado: {hoje}", md, count=1, flags=re.M)
        md = re.sub(r"^modelo_base: .*$", f"modelo_base: {modelo}", md, count=1, flags=re.M)
        md = re.sub(r"## Histórico\n.*", f"## Histórico\n\n{NAO_PUBLICADO}\n- Primeira versão, a partir do plugin {modelo}.\n", md, flags=re.S)
        (destino / f"{slug}.md").write_text(md, encoding="utf-8")
        (destino / "exemplo.json").write_text((origem / "exemplo.json").read_text(encoding="utf-8"), encoding="utf-8")
    else:
        md = MODELO_MD.read_text(encoding="utf-8").replace("{{slug}}", slug).replace("{{data}}", hoje)
        (destino / f"{slug}.md").write_text(md, encoding="utf-8")
        (destino / f"{slug}.json").write_text(json.dumps({"formato": "waipe-paginas/1", "slug": slug, "versao": "0.0.0"}, indent=2) + "\n", encoding="utf-8")
        (destino / "exemplo.json").write_text("[]\n", encoding="utf-8")
    print(f"Criado {destino.relative_to(RAIZ)}/ ({'a partir de ' + modelo if modelo else 'em branco'}). Complete o .json, o .md e o exemplo.json e rode 'validar'.")


def cmd_salvar(_args):
    # Um caminho só para enviar: waipe.py salvar valida agentes e plugins.
    r = subprocess.run([sys.executable, str(WAIPE / "waipe.py"), "salvar"], cwd=RAIZ)
    sys.exit(r.returncode)


def gerar_previas(lista):
    """Roda previa.mjs (motor do waipe-paginas). Devolve True se gerou, False se o motor não está disponível."""
    if not lista:
        return True
    r = subprocess.run(["node", str(FERRAMENTA / "previa.mjs"), *map(str, lista)], cwd=RAIZ, capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    if r.returncode == 3:
        return False
    if r.returncode != 0:
        erro("não foi possível gerar as prévias.")
    return True


def cmd_gerar_modelos(args):
    lista = []
    for slug in args:
        p = achar(slug)
        if not p:
            erro(f"plugin '{slug}' não existe.")
        lista.append(p)
    # Sem slug: no template, o catálogo; no cliente, só os plugins dele (o catálogo é do framework).
    if not gerar_previas(lista or (_dirs(CATALOGO) if modo_template() else pastas())):
        sys.exit(1)


def cmd_release(args):
    if len(args) != 2:
        erro("uso: release <slug> <patch|minor|major|X.Y.Z>")
    slug, pedido = args
    template = modo_template()
    pasta = base_trabalho() / slug
    rel = pasta.relative_to(RAIZ).as_posix()
    js, md = pasta / f"{slug}.json", pasta / f"{slug}.md"
    if not md.exists() or not js.exists():
        erro(f"{rel} não tem o par .json + .md.")
    exigir_main_limpa()
    puxar()
    anterior = "" if template else ultima_tag(f"{PREFIXO_TAG}{slug}/")
    if anterior and not mudou_desde(anterior, rel):
        erro(f"nada mudou em {rel}/ desde {anterior}.")
    texto = md.read_text(encoding="utf-8")
    fm = frontmatter(texto) or {}
    base = anterior.split("/v")[-1] if anterior else fm.get("versao", "0.0.0")
    versao = "1.0.0" if base == "0.0.0" and pedido in NIVEIS else proxima(base, pedido)
    tag = f"{PREFIXO_TAG}{slug}/v{versao}"
    if not template and git("ls-remote", "--tags", "origin", f"refs/tags/{tag}", checar=False):
        erro(f"a tag {tag} já existe.")
    hoje = datetime.date.today().isoformat()
    cab = f"### v{versao} ({hoje})"
    if NAO_PUBLICADO in texto:
        texto = texto.replace(NAO_PUBLICADO, cab, 1)
    else:
        texto = re.sub(r"^## Histórico\n\n", f"## Histórico\n\n{cab}\n- Release sem notas.\n\n", texto, count=1, flags=re.M)
    texto = re.sub(r"^versao: .*$", f"versao: {versao}", texto, count=1, flags=re.M)
    texto = re.sub(r"^atualizado: .*$", f"atualizado: {hoje}", texto, count=1, flags=re.M)
    md.write_text(texto, encoding="utf-8")
    js.write_text(re.sub(r'"versao": "[^"]*"', f'"versao": "{versao}"', js.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    erros, _ = validar_pasta(pasta)
    erros += (validar_motor([pasta]) or {}).get(slug, {}).get("erros", [])
    if erros:
        git("checkout", "--", str(md), str(js))
        erro("o plugin não passou na validação:\n- " + "\n- ".join(erros))
    if not gerar_previas([pasta]):
        print("aviso: prévias do simulador não geradas (sem o waipe-paginas ao lado).")
    git("add", "--", rel)
    if template:
        git("commit", "-q", "-m", f"feat(catalogo): plugin {slug} {versao}")
        print(f"Plugin do catálogo {slug} em {versao} (commit feito). Escreva a linha em '## Não publicado' do "
              ".claude/waipe/CHANGELOG.md e publique com: waipe.py release-framework <nivel>")
        return
    git("commit", "-q", "-m", f"release({slug}): v{versao}")
    git("push", "origin", "main")
    nome = fm.get("nome", slug)
    git("tag", "-a", tag, "-m", f"{nome} v{versao}")
    git("push", "origin", tag)
    notas = secao_historico(texto, versao) + f"\n\nPlataforma: Waipe Páginas v{fm.get('plataforma', '?')} ou mais nova. Instale o {slug}.json em Configurações gerais > Páginas."
    arquivos = [str(a.relative_to(RAIZ)) for a in sorted(pasta.rglob("*")) if a.is_file()]
    url = gh("release", "create", tag, *arquivos, "--title", f"{nome} v{versao}", "--notes", notas, "--verify-tag")
    print(f"Release fechada: {tag}\n{url}\nAnexos: {', '.join(Path(a).name for a in arquivos)}")


COMANDOS = {"status": cmd_status, "validar": cmd_validar, "catalogo": cmd_catalogo, "novo": cmd_novo, "salvar": cmd_salvar,
            "release": cmd_release, "gerar-modelos": cmd_gerar_modelos, "hook": cmd_hook}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    COMANDOS[sys.argv[1]](sys.argv[2:])
