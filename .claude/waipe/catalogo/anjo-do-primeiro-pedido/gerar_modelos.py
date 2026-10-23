# -*- coding: utf-8 -*-
"""Modelos de comunicação do Anjo do Primeiro Pedido: roda os nodes reais com dados fictícios (nada é enviado).
As listas de clientes vêm das planilhas já salvas em modelos/planilhas/. Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, nome_na_planilha, pagina_whatsapp, planilhas_salvas, gravar, rodar_node, salvar_manifesto, slug_de

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
URL = 'https://docs.google.com/spreadsheets/d/exemplo-'

planilhas = planilhas_salvas(SAIDA)
vendedores = []
for i, (_, titulo, colunas, linhas) in enumerate(planilhas):
    nome = nome_na_planilha(titulo)
    clientes = [dict(zip(colunas, l)) for l in linhas]
    vendedores.append(dict(codigo=str(101 + i), nome=nome, telefone='(11) 9%04d-%04d' % (4100 + i, 1000 + i),
                           email=slug_de(nome).replace('-', '.') + '@empresa.exemplo.com.br', quantidade=len(clientes), clientes=clientes))
vendedores.sort(key=lambda v: (-v['quantidade'], v['nome']))
for i, v in enumerate(vendedores):
    v['posicao'] = i + 1
radar = dict(total=sum(v['quantidade'] for v in vendedores), totalVendedores=len(vendedores), diasRadar=20, diasMaximoRadar=40,
             data='20/10/2026', dataTitulo='20-10-2026', aba='Página1', semContato=[], vendedores=vendedores)

helena = next(v for v in vendedores if v['nome'] == 'Helena Prado')
url_helena = URL + slug_de(helena['nome'])
vend = rodar_node(FLOW, 'Montar Mensagens do Vendedor', {'node': {
    'Processar Radar': radar, 'Cada Vendedor': helena, 'Criar Planilha do Vendedor': {'spreadsheetUrl': url_helena}}})[0]
gravar(SAIDA, 'email-vendedor.html', vend['corpo_email'])
gravar(SAIDA, 'whatsapp-vendedor.html', pagina_whatsapp(
    [dict(texto=vend['mensagem_whatsapp'], link=dict(titulo=planilhas[[nome_na_planilha(p[1]) for p in planilhas].index('Helena Prado')][1],
                                                      host='docs.google.com', href='planilhas/helena-prado.html'))],
    'Empresa Exemplo · Comercial', '07:00', 'TERÇA-FEIRA', {url_helena: 'planilhas/helena-prado.html'}, 'WhatsApp do vendedor'))
indice = [{'json': {'values': [['Vendedor', 'Link']] + [[v['nome'], URL + slug_de(v['nome'])] for v in vendedores]}}]
ges = rodar_node(FLOW, 'Montar E-mail do Gestor', {'items': indice, 'node': {'Processar Radar': radar}})[0]
gravar(SAIDA, 'consolidado-gestor.html', ges['corpo_html'])

DE = 'Relatórios Waipe <relatorios@empresa.exemplo.com.br>'
salvar_manifesto(SAIDA, [
    dict(arquivo='whatsapp-vendedor.html', tipo='whatsapp', rotulo='WhatsApp do vendedor', contato='Empresa Exemplo · Comercial',
         data='TERÇA-FEIRA', quem='Cada vendedor'),
    dict(arquivo='email-vendedor.html', tipo='email', rotulo='E-mail do vendedor', assunto=vend['assunto_email'], de=DE,
         para='Helena Prado <%s>' % helena['email'], data='ter., 20 out. 07:02', quem='Cada vendedor com e-mail'),
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='Consolidado do gestor', assunto=ges['assunto'], de=DE,
         para='Nome do Gestor <gestor@empresa.exemplo.com.br>', data='ter., 20 out. 07:09', quem='Gestor comercial'),
] + [dict(arquivo=a, tipo='planilha', rotulo='Planilha de ' + nome_na_planilha(t)) for a, t, _, _ in planilhas])
