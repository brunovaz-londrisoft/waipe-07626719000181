# -*- coding: utf-8 -*-
"""Modelos de comunicação do Produtos sem Giro: roda os nodes reais com dados fictícios (nada é enviado).
Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import gravar, modelo_do_arquivo, pagina_planilha, rodar_node, salvar_manifesto

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
HOJE = '2026-10-23'
EMPRESAS = [('ALFA DISTRIBUIDORA LTDA', '11222333000101'), ('BETA COMERCIO LTDA', '44555666000102')]
# código, descrição, grupo, subgrupo, custo médio, custo de aquisição, preço de venda
CATALOGO = [('3001', 'Detergente neutro 5L', 'LIMPEZA', 'DETERGENTES', 22.4, 21.0, 38.9), ('3002', 'Papel toalha interfolha', 'DESCARTAVEIS', 'PAPEL', 31.2, 30.0, 54.0),
            ('3003', 'Desinfetante lavanda 5L', 'LIMPEZA', 'DESINFETANTES', 18.9, 18.0, 31.5), ('3004', 'Luva nitrílica caixa', 'EPI', 'LUVAS', 27.5, 26.0, 42.0),
            ('3005', 'Saco de lixo 100L', 'DESCARTAVEIS', 'SACOS', 15.1, 14.5, 27.8), ('3006', 'Álcool 70% 1L', 'LIMPEZA', 'ALCOOL', 6.3, 6.0, 9.9),
            ('3007', 'Pano multiuso rolo', 'LIMPEZA', 'PANOS', 0, 36.0, 64.5), ('3008', 'Copo descartável 200ml', 'DESCARTAVEIS', 'COPOS', 11.2, 10.8, 18.4),
            ('3009', 'Enceradeira industrial', 'EQUIPAMENTOS', 'MAQUINAS', 2890.0, 2750.0, 4100.0), ('3010', 'Carrinho funcional', 'EQUIPAMENTOS', 'CARRINHOS', 640.0, 610.0, 980.0),
            ('3011', 'Mop giratório', 'UTENSILIOS', 'MOPS', 48.0, 45.0, 79.9), ('3012', 'Dispenser sabonete', 'UTENSILIOS', 'DISPENSERS', 37.0, 35.0, 59.0),
            ('3013', 'Cera líquida 5L', 'LIMPEZA', 'CERAS', 44.0, 42.0, 71.0), ('3014', 'Limpa vidros 5L', 'LIMPEZA', 'VIDROS', 26.0, 25.0, 44.0)]
# Dias desde a última venda (None = sem venda na janela); os de 20 dias ou mais entram no alerta
ULTIMA = {'3001': 2, '3002': 1, '3003': 5, '3004': 9, '3005': 3, '3006': 1, '3007': 24, '3008': 4, '3009': None, '3010': 27,
          '3011': 22, '3012': None, '3013': 26, '3014': 12}


def dia(n):
    import datetime
    return (datetime.date.fromisoformat(HOJE) - datetime.timedelta(days=n)).isoformat()


def entradas(sem_parados=False):
    estoque, vendas = [], []
    for e, (razao, cnpj) in enumerate(EMPRESAS):
        for i, (cod, nome, grupo, sub, medio, aquis, preco) in enumerate(CATALOGO):
            estoque.append(dict(codigo=cod, nome=nome, grupo=grupo, subgrupo=sub, quantidade=3 + (i * 5 + e * 3) % 40,
                                custo_medio=medio, custo_aquisicao=aquis, _razaoOrigem=razao, _cnpjOrigem=cnpj))
            ultimo = 1 if sem_parados else ULTIMA[cod]
            if ultimo is None:
                continue
            for v in range(1 + (i + e) % 4):
                qtd = 2 + (i * 3 + v * 7 + e) % 15
                vendas.append(dict(produto=cod, nomproduto=nome, quantidade=qtd, total_venda=round(qtd * preco, 2),
                                   lucro=round(qtd * (preco - aquis), 2), data_venda=dia(ultimo + v * 9 if v else ultimo),
                                   _razaoOrigem=razao, _cnpjOrigem=cnpj))
    return [{'json': {'dados': [{'dados': estoque}]}}, {'json': {'dados': [{'dados': vendas}]}}]


calc = rodar_node(FLOW, 'Calcular produtos sem giro', {'items': entradas(), 'hoje': HOJE})[0]
url = 'https://docs.google.com/spreadsheets/d/exemplo-produtos-sem-giro'
alerta = rodar_node(FLOW, 'Montar E-mail de Alerta', {'node': {'Calcular produtos sem giro': calc, 'Criar planilha': {'spreadsheetUrl': url}}})[0]
mais = rodar_node(FLOW, 'Montar E-mail dos Mais Vendidos', {'node': {'Calcular produtos sem giro': calc}})[0]
calc_vazio = rodar_node(FLOW, 'Calcular produtos sem giro', {'items': entradas(sem_parados=True), 'hoje': HOJE})[0]
vazio = rodar_node(FLOW, 'Montar E-mail sem Produtos Parados', {'node': {'Calcular produtos sem giro': calc_vazio}})[0]

gravar(SAIDA, 'email-alerta-sem-giro.html', alerta['corpo_html'])
gravar(SAIDA, 'email-mais-vendidos.html', mais['corpo_html'])
gravar(SAIDA, 'email-sem-produtos-parados.html', vazio['corpo_html'])
colunas = list(calc['linhas'][0].keys())
gravar(SAIDA, 'planilhas/produtos-sem-giro.html', pagina_planilha('Produtos sem giro - %s' % HOJE, colunas,
                                                                  [[l[c] for c in colunas] for l in calc['linhas']], 'Página1',
                                                                  [80, 240, 130, 130, 130, 150, 150, 170, 120, 220, 320]))

DE = 'Relatórios Waipe <relatorios@empresa.exemplo.com.br>'
PARA = 'Compras <compras@empresa.exemplo.com.br>'
salvar_manifesto(SAIDA, [
    dict(arquivo='email-alerta-sem-giro.html', tipo='email', rotulo='Alerta de produtos sem giro', assunto=alerta['assunto'], de=DE, para=PARA,
         data='sex., 23 out. 07:00', quem='Compras e gestão de estoque'),
    dict(arquivo='email-mais-vendidos.html', tipo='email', rotulo='Mais vendidos e reposição', assunto=mais['assunto'], de=DE, para=PARA,
         data='sex., 23 out. 07:00', quem='Compras e gestão de estoque'),
    dict(arquivo='email-sem-produtos-parados.html', tipo='email', rotulo='Aviso: nenhum produto parado', assunto=vazio['assunto'], de=DE, para=PARA,
         data='sex., 23 out. 07:00', quem='Compras (quando não há produto parado)'),
    dict(arquivo='planilhas/produtos-sem-giro.html', tipo='planilha', rotulo='Planilha de produtos sem giro', quem='Compras e gestão de estoque'),
])
