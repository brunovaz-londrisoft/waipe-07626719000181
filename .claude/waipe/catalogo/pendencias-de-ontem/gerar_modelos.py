# -*- coding: utf-8 -*-
"""Modelos de comunicação do Pendências de Ontem: roda o node real do e-mail com dados fictícios (nada é enviado).
Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, gravar, rodar_node, salvar_manifesto

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
HOJE = '2026-10-22'
VEND = ['Helena Prado', 'Otávio Brandão', 'Larissa Nunes']


def mov(n, data, cliente, status, valor, nf='NAO', v=0):
    return dict(numero=str(n), data=data + 'T10:00:00', status=status, cliente=cliente, vendedor=VEND[v % 3], valor=valor, tem_nf=nf, nf_numero='')


def conta(campo_nome, nome, doc, parcela, venc, valor, campo_saldo):
    return {campo_nome: nome, 'lancamento': doc, 'parcela': parcela, 'datavencimento': venc + 'T00:00:00', 'datapagamento': '', campo_saldo: valor}


vendas = [mov(4512, '2026-10-14', 'Panificadora Aurora', 'ORCAMENTO', 1850.40), mov(4520, '2026-10-17', 'Mercearia Bela Vista', 'ORCAMENTO', 920.00, v=1),
          mov(4527, '2026-10-21', 'Doceria Primavera', 'ORCAMENTO', 2310.75, v=2), mov(4498, '2026-10-09', 'Confeitaria Estrela', 'VENDA', 5420.00),
          mov(4515, '2026-10-20', 'Minimercado Campo Belo', 'VENDA', 1288.90, v=1), mov(4530, '2026-10-21', 'Cafeteria Vila Verde', 'VENDA', 760.00, nf='SIM', v=2),
          mov(4531, '2026-10-22', 'Lanchonete Lírio', 'ORCAMENTO', 430.00)]
os_ = [mov(812, '2026-10-16', 'Bomboniere Beira Rio', 'ORCAMENTO', 640.00, v=1), mov(815, '2026-10-20', 'Padaria Sol Nascente', 'ORCAMENTO', 1150.00, v=2),
       mov(806, '2026-10-13', 'Mercearia Ouro Verde', 'OS', 2890.00)]
pagar = [conta('nomfornece', 'Distribuidora Exemplo Ltda', 'NF 10233', '2/3', '2026-10-18', 4380.00, 'remanescente'),
         conta('nomfornece', 'Embalagens Modelo', 'NF 5521', '1/1', '2026-10-21', 980.50, 'remanescente'),
         conta('nomfornece', 'Transportadora Fictícia', 'CT 7781', '1/2', '2026-10-22', 1240.00, 'remanescente')]
receber = [conta('nomcliente', 'Panificadora Aurora', 'DUP 3301', '3/4', '2026-10-15', 1620.00, 'saldo'),
           conta('nomcliente', 'Confeitaria Estrela', 'DUP 3290', '2/2', '2026-10-19', 2710.00, 'saldo'),
           conta('nomcliente', 'Minimercado Campo Belo', 'DUP 3315', '1/3', '2026-10-21', 430.00, 'saldo'),
           conta('nomcliente', 'Mercearia Bela Vista', 'DUP 3320', '1/1', '2026-10-22', 920.00, 'saldo'),
           conta('nomcliente', 'Doceria Primavera', 'DUP 3322', '1/2', '2026-10-22', 1155.38, 'saldo')]
rel = lambda linhas: {'dados': [{'dados': linhas, 'erros': []}]}
out = rodar_node(FLOW, 'Montar E-mail de Pendências', {'node': {
    'Vendas da Semana': rel(vendas), 'O.S. da Semana': rel(os_), 'Contas a Pagar da Semana': rel(pagar),
    'Contas a Receber da Semana': rel(receber)}, 'agora': HOJE + 'T11:00:00.000Z'})[0]
gravar(SAIDA, 'consolidado-gestor.html', out['html'])

salvar_manifesto(SAIDA, [
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='E-mail diário de pendências', assunto=out['assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Nome do Responsável <responsavel@empresa.exemplo.com.br>',
         data='qua., 22 out. 08:00', quem='Responsável pela rotina da manhã'),
])
