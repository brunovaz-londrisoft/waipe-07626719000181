# -*- coding: utf-8 -*-
"""Modelos de comunicação do Guardião da Carteira: roda os nodes reais com dados fictícios (nada é enviado).
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
    slug = 'guardiao-da-carteira'
    saida = SAIDA
    hoje = datetime.date.today()
    nomes = ['Mercado Aurora', 'Condomínio Bela Vista', 'Hotel Primavera', 'Clínica Ouro Verde', 'Restaurante Sol Nascente',
             'Academia Vila Verde', 'Colégio Estrela', 'Supermercado Campo Belo', 'Indústria Lírio', 'Hospital Beira Rio',
             'Padaria Bom Pão', 'Lavanderia Água Clara', 'Creche Pequeno Príncipe', 'Shopping Exemplo', 'Prefeitura de Cidade Exemplo',
             'Associação Exemplo', 'Transportadora Rota Certa', 'Pousada Recanto', 'Laboratório Vida', 'Mercearia do Bairro']
    vend = ['Helena Prado', 'Otávio Brandão', 'Larissa Nunes']
    dias = [3, 8, 12, 20, 25, 28, 35, 41, 47, 55, 64, 70, 78, 85, 95, 120, 180, 240, None, None]
    dl, contatos, inter = [], [], []
    for i, nome in enumerate(nomes):
        doc = '%02d%03d%03d0001%02d' % (11 + i, 222 + i, 333 + i, 10 + i)
        d = dias[i]
        dl.append(dict(codigo=str(5000 + i), nome_razao_social=nome.upper(), cnpj_cpf=doc, tipo_pessoa='Jurídica',
                       email='contato@%s.exemplo.com.br' % arq(nome).replace('-', ''), telefone='(11) 9%04d-%04d' % (8100 + i, 1200 + i),
                       vendedor=vend[i % 3], empresa='EMPRESA EXEMPLO LTDA',
                       data_ultima_venda=(hoje - datetime.timedelta(days=d)).isoformat() if d is not None else None))
        if i % 3 != 2:
            contatos.append(dict(Id=900 + i, Name=nome, CNPJ=doc, Email='', Phones=[]))
            inter.append(dict(ContactId=900 + i, Date=(hoje - datetime.timedelta(days=(i * 7) % 60 + 1)).isoformat() + 'T10:00:00-03:00'))
    items = [{'json': {'dados': [{'dados': dl}]}}, {'json': {'status': 200, 'parsedBody': {'value': contatos}}}]
    cons = rodar_node(flow(slug), 'Consolidar Clientes e Calcular Status', {'items': items, 'node': {'Buscar Interações Ploomes (18 meses)': {'parsedBody': {'value': inter}}}})[0]
    ctx = {'Consolidar Clientes e Calcular Status': cons, 'Criar Planilha do Resultado': {'spreadsheetUrl': url('monitoramento carteira')}}
    em = rodar_node(flow(slug), 'Montar E-mail do Relatório', {'node': ctx})[0]
    gravar(saida, 'relatorio-gestor.html', em['corpo_html'])
    mapa = node(slug, 'Preencher Planilha com Clientes')['parameters']['columnMappings']
    colunas = [m['column'] for m in mapa]
    campos = [re.search(r'\$json\.(\w+)', m['value']).group(1) for m in mapa]
    # A planilha mostra o documento mascarado (como o flow grava); os CNPJs fictícios não são de ninguém.
    linhas = [[l.get(c, '') for c in campos] for l in cons['linhas']]
    titulo = preencher_titulo(node(slug, 'Criar Planilha do Resultado')['parameters']['title'], ctx)
    gravar(saida, 'planilhas/monitoramento-da-carteira.html', pagina_planilha(titulo, colunas, linhas, 'Página1', [130] * len(colunas)))
    salvar_manifesto(saida, [
        dict(arquivo='relatorio-gestor.html', tipo='email', rotulo='Relatório do gestor', assunto=em['assunto'], de=DE,
             para='Nome do Gestor <gestor@empresa.exemplo.com.br>', data='sex., 17:00', quem='Gestor comercial'),
        dict(arquivo='planilhas/monitoramento-da-carteira.html', tipo='planilha', rotulo='Planilha da carteira', quem='Gestor comercial'),
    ])


gerar()
