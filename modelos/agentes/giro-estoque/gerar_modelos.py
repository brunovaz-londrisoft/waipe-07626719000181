# -*- coding: utf-8 -*-
"""Modelos de comunicação do Giro de Estoque: roda o node real do e-mail com dados fictícios (nada é enviado).
Os produtos vêm das planilhas já salvas em modelos/planilhas/. Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '.claude', 'waipe', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, nome_na_planilha, pagina_planilha, planilhas_salvas, gravar, rodar_node, salvar_manifesto, slug_de

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
URL = 'https://docs.google.com/spreadsheets/d/exemplo-'
ACAO = ['🔴 Ruptura — comprar já', '🟠 Comprar urgente']
ORDEM = ['🔴 Ruptura — comprar já', '🟠 Comprar urgente', '🟡 Comprar', '🟢 Estoque saudável', '🔵 Excesso de estoque',
         '⚫ Estoque parado (sem giro)', '⚪ Zerado sem giro']

CONSOLIDADA = 'planilhas/consolidado.html'  # gerada abaixo; não é fonte de fabricante
planilhas = [x for x in planilhas_salvas(SAIDA) if x[0] != CONSOLIDADA]
fabricantes, status, total_sug = [], {}, 0
for _, titulo, colunas, linhas in planilhas:
    prods = [dict(zip(colunas, l)) for l in linhas]
    col_sug = next(c for c in colunas if c.startswith('Sugestão'))
    sug = sum(int(p[col_sug] or 0) for p in prods)
    total_sug += sug
    for p in prods:
        status[p['Status']] = status.get(p['Status'], 0) + 1
    fabricantes.append(dict(nome=nome_na_planilha(titulo), quantidade=len(prods), acao_imediata=sum(1 for p in prods if p['Status'] in ACAO),
                            sugestao=sug, produtos=prods))
fabricantes.sort(key=lambda f: (-f['acao_imediata'], -f['quantidade'], f['nome']))
for i, f in enumerate(fabricantes):
    f['posicao'] = i + 1
resumo = [dict(status=s, quantidade=status[s]) for s in ORDEM if s in status] + [dict(status=s, quantidade=q) for s, q in status.items() if s not in ORDEM]
dados = dict(data='19/10/2026', dataTitulo='19-10-2026', aba='Página1', total_produtos=sum(f['quantidade'] for f in fabricantes),
             total_fabricantes=len(fabricantes), total_acao_imediata=sum(f['acao_imediata'] for f in fabricantes), dias_projecao=45,
             total_sugestao=total_sug, resumo_status=resumo, fabricantes=fabricantes)
# Planilha consolidada: mesmas colunas, com Fabricante logo depois de Produto (como o node Montar Consolidado)
cols = planilhas[0][2]
cols_c = cols[:2] + ['Fabricante'] + cols[2:]
linhas_c = [[p[c] for c in cols[:2]] + [f['nome']] + [p[c] for c in cols[2:]] for f in fabricantes for p in f['produtos']]
gravar(SAIDA, CONSOLIDADA, pagina_planilha('Giro de Estoque - Consolidado - 19-10-2026', cols_c, linhas_c, 'Página1',
                                            [80, 260, 200] + [130] * (len(cols_c) - 3)))
resumo_c = dict(ok=True, url=URL + 'consolidado', total=len(linhas_c))
def indice(fabs):
    return [{'json': {'values': [['Fabricante', 'Produtos', 'Link']] + [[f['nome'], f['quantidade'], URL + slug_de(f['nome'])] for f in fabs]}}]
ges = rodar_node(FLOW, 'Montar E-mail', {'items': indice(fabricantes), 'node': {'Montar Fabricantes': dados, 'Resumo Consolidado': resumo_c}})[0]
gravar(SAIDA, 'consolidado-gestor.html', ges['corpo_html'])
# Variante: o segundo fabricante falhou no loop (ex.: erro 429 do Google Sheets) e não entrou no índice
falhou = fabricantes[1]['nome']
err = rodar_node(FLOW, 'Montar E-mail', {'items': indice([f for f in fabricantes if f['nome'] != falhou]), 'node': {'Montar Fabricantes': dados, 'Resumo Consolidado': resumo_c}})[0]
gravar(SAIDA, 'consolidado-gestor-com-erro.html', err['corpo_html'])

salvar_manifesto(SAIDA, [
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='Consolidado do gestor', assunto=ges['assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Nome do Gestor <gestor@empresa.exemplo.com.br>',
         data='seg., 19 out. 07:34', quem='Gestor'),
    dict(arquivo='consolidado-gestor-com-erro.html', tipo='email', rotulo='Consolidado do gestor (fabricante sem planilha)', assunto=err['assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Nome do Gestor <gestor@empresa.exemplo.com.br>',
         data='seg., 19 out. 07:34', quem='Gestor'),
] + [dict(arquivo=CONSOLIDADA, tipo='planilha', rotulo='Planilha consolidada (todos os fabricantes)')] + [dict(arquivo=a, tipo='planilha', rotulo='Planilha de ' + nome_na_planilha(t)) for a, t, _, _ in planilhas])
