# -*- coding: utf-8 -*-
"""Modelos de comunicação do Comissão Mensal - Gerência e Vendedores: roda os nodes reais com dados fictícios (nada é enviado).
Rode: python3 gerar_modelos.py"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import gravar, modelo_do_arquivo, pagina_planilha, rodar_node, salvar_manifesto, slug_de

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
DE = 'Relatórios Waipe <relatorios@empresa.exemplo.com.br>'


def flow(_slug):
    return FLOW


def node(_slug, nome):
    return next(n for n in json.load(open(FLOW, encoding='utf-8'))['nodes'] if n['name'] == nome)


def arq(nome):
    return slug_de(nome)


def url(nome):
    return 'https://docs.google.com/spreadsheets/d/exemplo-' + arq(nome)


def preencher_titulo(modelo, ctx):
    return re.sub(r'\{\{\s*\$node\[\s*"([^"]+)"\s*\]\.json\.(\w+)\s*\}\}', lambda m: str(ctx[m.group(1)][m.group(2)]), modelo)


def gerar():
    slug = 'comissao-mensal-gerencia-vendedores'
    saida = SAIDA
    vendedores = [('Helena Prado', 'helena.prado@empresa.exemplo.com.br'), ('Otávio Brandão', 'otavio.brandao@empresa.exemplo.com.br'),
                  ('Larissa Nunes', 'larissa.nunes@empresa.exemplo.com.br'), ('Davi Calheiros', 'davi.calheiros@empresa.exemplo.com.br'),
                  ('Sabrina Teles', '')]
    clientes = ['Mercado Aurora', 'Condomínio Bela Vista', 'Hotel Primavera', 'Clínica Ouro Verde', 'Restaurante Sol Nascente',
                'Academia Vila Verde', 'Colégio Estrela', 'Supermercado Campo Belo', 'Indústria Lírio', 'Hospital Beira Rio']
    regras = ['Tabela de Comissão: 5,00%', 'Tabela de Comissão: 4,80%', 'Tabela de Comissão: 4,50%']
    vendas, n = [], 0
    for k, (nome, _) in enumerate(vendedores):
        for i in range(6 - k):
            n += 1
            sub = round(1800 + (n * 937 % 7400) + i * 113.5, 2)
            desc_pct = [0, 3, 7][(n + k) % 3]
            desc = round(sub * desc_pct / 100, 2)
            liq = round(sub - desc, 2)
            pct = [5.0, 4.8, 4.5][(n + k) % 3]
            vendas.append(dict(nome_vendedor=nome, numero_venda=48000 + n, numero_nota=9100 + n, data_venda='2026-10-%02d' % (2 + (n * 5) % 25),
                               data_emissao_nf='2026-10-%02d' % (3 + (n * 5) % 25), nome_cliente=clientes[(n + k) % len(clientes)],
                               subtotal_venda=sub, valor_total_venda=liq, valor_total_desconto=desc, percentual_desconto_usado=desc_pct,
                               valor_comissao=round(liq * pct / 100, 2), regra_comissao_aplicada=regras[(n + k) % 3], razao_origem='EMPRESA EXEMPLO LTDA'))
    cadastro = [{'json': {'dados': [{'dados': [{'nomvendedor': nome, 'email': email} for nome, email in vendedores]}]}}]
    cons = rodar_node(flow(slug), 'Consolidar Comissões', {'items': cadastro, 'node': {'Agregar Vendas': {'vendas': vendas}}, 'hoje': '2026-10-31'})[0]
    ger = rodar_node(flow(slug), 'Montar E-mail da Gerência', {'node': {'Consolidar Comissões': cons, 'Criar Planilha Geral': {'spreadsheetUrl': url('comissoes geral')}}})[0]
    gravar(saida, 'consolidado-gerencia.html', ger['corpo_html'])
    v0 = cons['vendedores'][0]
    ven = rodar_node(flow(slug), 'Montar E-mail do Vendedor', {'node': {'Consolidar Comissões': cons, 'Um Vendedor por Vez': v0,
                                                                         'Criar Planilha do Vendedor': {'spreadsheetUrl': url(v0['nome'])}}})[0]
    gravar(saida, 'email-vendedor.html', ven['corpo_html'])
    colunas = list(cons['linhas'][0].keys())
    larg = [100, 95, 110, 110, 220, 130, 140, 150, 100, 130, 200, 140, 210]
    linhas = lambda f: [[l[c] for c in colunas] for l in cons['linhas'] if f(l)]
    gravar(saida, 'planilhas/geral.html', pagina_planilha(cons['titulo_planilha_geral'], colunas, linhas(lambda l: True), 'Página1', larg))
    pls = [dict(arquivo='planilhas/geral.html', tipo='planilha', rotulo='Planilha geral da gerência', quem='Gerência')]
    for v in cons['vendedores']:
        a = 'planilhas/%s.html' % arq(v['nome'])
        gravar(saida, a, pagina_planilha(v['titulo_planilha'], colunas, linhas(lambda l, nm=v['nome']: l['Nome do Vendedor'] == nm), 'Página1', larg))
        pls.append(dict(arquivo=a, tipo='planilha', rotulo='Planilha de ' + v['nome'], quem=v['nome']))
    salvar_manifesto(saida, [
        dict(arquivo='email-vendedor.html', tipo='email', rotulo='E-mail do vendedor', assunto=ven['assunto'], de=DE,
             para='%s <%s>' % (v0['nome'], v0['email']), data='sáb., 31 out. 23:30', quem='Cada vendedor com e-mail'),
        dict(arquivo='consolidado-gerencia.html', tipo='email', rotulo='Ranking da gerência', assunto=ger['assunto'], de=DE,
             para='Gerência <gerencia@empresa.exemplo.com.br>', data='sáb., 31 out. 23:30', quem='Gerência'),
    ] + pls)


gerar()
