# -*- coding: utf-8 -*-
"""Modelos de comunicação do CMV Mensal: roda os nodes reais com dados fictícios (nada é enviado).
Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import gravar, modelo_do_arquivo, pagina_planilha, rodar_node, salvar_manifesto

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
HOJE = '2026-10-01'  # sem período no corpo do webhook, o flow calcula o mês anterior completo (setembro)
EMPRESAS = [('ALFA DISTRIBUIDORA LTDA', '11222333000101'), ('BETA COMERCIO LTDA', '44555666000102')]
PRODUTOS = [('2001', 'Detergente neutro 5L', 'LIMPEZA', 'DETERGENTES', 38.9, 0.62), ('2002', 'Papel toalha interfolha', 'DESCARTAVEIS', 'PAPEL', 54.0, 0.58),
            ('2003', 'Desinfetante lavanda 5L', 'LIMPEZA', 'DESINFETANTES', 31.5, 0.6), ('2004', 'Luva nitrílica caixa', 'EPI', 'LUVAS', 42.0, 0.66),
            ('2005', 'Saco de lixo 100L', 'DESCARTAVEIS', 'SACOS', 27.8, 0.55), ('2006', 'Álcool 70% 1L', 'LIMPEZA', 'ALCOOL', 9.9, 0.64),
            ('2007', 'Pano multiuso rolo', 'LIMPEZA', 'PANOS', 64.5, 0.57), ('2008', 'Copo descartável 200ml', 'DESCARTAVEIS', 'COPOS', 18.4, 0.61)]

linhas = []
for mes, dias in (('2026-07', 31), ('2026-08', 31), ('2026-09', 30)):
    for e, (razao, cnpj) in enumerate(EMPRESAS):
        for p, (cod, nome, grupo, sub, preco, custo) in enumerate(PRODUTOS):
            for v in range(2 + (p + e) % 3):
                qtd = 3 + (p * 7 + v * 5 + e * 3) % 20
                total = round(qtd * preco, 2)
                linha = dict(data_venda='%s-%02d' % (mes, 1 + (p * 3 + v * 7 + e) % dias), produto=cod, nomproduto=nome, grupo=grupo, subgrupo=sub,
                             quantidade=qtd, total_venda=total, total_custo=round(total * custo, 2), _razaoOrigem=razao, _cnpjOrigem=cnpj)
                linhas.append(linha)
# Uma venda sem custo e uma devolução: aparecem nos avisos do e-mail
linhas.append(dict(data_venda='2026-09-18', produto='2009', nomproduto='Rodo 60cm', grupo='UTENSILIOS', subgrupo='RODOS', quantidade=4,
                   total_venda=159.6, _razaoOrigem=EMPRESAS[0][0], _cnpjOrigem=EMPRESAS[0][1]))
linhas.append(dict(data_venda='2026-09-22', produto='2001', nomproduto='Detergente neutro 5L', grupo='LIMPEZA', subgrupo='DETERGENTES', quantidade=-2,
                   total_venda=-77.8, total_custo=-48.24, _razaoOrigem=EMPRESAS[1][0], _cnpjOrigem=EMPRESAS[1][1]))

calc = rodar_node(FLOW, 'Calcular CMV', {'items': [{'json': {'dados': [{'dados': linhas}]}}], 'node': {'Receber período': {}}, 'hoje': HOJE})[0]
email = rodar_node(FLOW, 'Montar E-mail do CMV', {'node': {'Calcular CMV': calc, 'Criar planilha CMV': {
    'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/exemplo-cmv'}}})[0]
gravar(SAIDA, 'email-cmv.html', email['corpo_html'])
colunas = list(calc['linhas'][0].keys())
gravar(SAIDA, 'planilhas/cmv.html', pagina_planilha('CMV %s a %s' % (calc['inicio'], calc['fim']), colunas,
                                                    [[l[c] for c in colunas] for l in calc['linhas']], 'Página1',
                                                    [90, 90, 240, 120, 120, 200, 80, 120, 120, 120, 100, 220]))

salvar_manifesto(SAIDA, [
    dict(arquivo='email-cmv.html', tipo='email', rotulo='E-mail do CMV do período', assunto=email['assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Diretoria <diretoria@empresa.exemplo.com.br>',
         data='qui., 1 out. 08:00', quem='Diretoria e compras'),
    dict(arquivo='planilhas/cmv.html', tipo='planilha', rotulo='Planilha do CMV', quem='Diretoria e compras'),
])
