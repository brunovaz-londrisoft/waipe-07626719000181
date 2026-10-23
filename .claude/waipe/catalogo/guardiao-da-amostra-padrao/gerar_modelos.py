# -*- coding: utf-8 -*-
"""Modelos de comunicação do Guardião da Amostra Padrão: roda os nodes reais com dados fictícios (nada é enviado).
As listas de clientes vêm das planilhas já salvas em modelos/planilhas/. Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, nome_na_planilha, planilhas_salvas, gravar, rodar_node, salvar_manifesto, slug_de

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
URL = 'https://docs.google.com/spreadsheets/d/exemplo-'

planilhas = planilhas_salvas(SAIDA)
vendedores = [dict(nome=nome_na_planilha(t), quantidade=len(linhas), clientes=[dict(zip(c, l)) for l in linhas]) for _, t, c, linhas in planilhas]
vendedores.sort(key=lambda v: (-v['quantidade'], v['nome']))
for i, v in enumerate(vendedores):
    v['posicao'] = i + 1
dados = dict(total=sum(v['quantidade'] for v in vendedores), totalVendedores=len(vendedores), diasSemComprar=40,
             data='15/10/2026', dataTitulo='15-10-2026', aba='Página1', vendedores=vendedores)
indice = [{'json': {'values': [['Vendedor', 'Link']] + [[v['nome'], URL + slug_de(v['nome'])] for v in vendedores]}}]
ges = rodar_node(FLOW, 'Montar E-mail Consolidado', {'items': indice, 'node': {'Processar Adormecidos': dados}})[0]
gravar(SAIDA, 'consolidado-gestor.html', ges['corpo_html'])

salvar_manifesto(SAIDA, [
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='Consolidado do gestor', assunto=ges['assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Nome do Gestor <gestor@empresa.exemplo.com.br>',
         data='qui., 15 out. 07:06', quem='Gestor comercial'),
] + [dict(arquivo=a, tipo='planilha', rotulo='Planilha de ' + nome_na_planilha(t)) for a, t, _, _ in planilhas])
