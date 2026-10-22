# -*- coding: utf-8 -*-
"""Exemplo mínimo de gerador dos modelos de comunicação de um agente (padrão v3). COPIE para a pasta temporária
(scratchpad), ADAPTE e rode de lá:

    python3 exemplo_gerar.py <pasta do repositório>        (ex.: python3 exemplo_gerar.py .)

Grava as peças em agentes/<SLUG>/modelos/ e o modelos.json. Os e-mails e o texto do WhatsApp saem do próprio node
(rodar_node executa só o JavaScript do node code, com as entradas fictícias abaixo; nada é enviado)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from comum import gravar, pagina_planilha, pagina_whatsapp, rodar_node, salvar_manifesto

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '.'
SLUG = 'meu-agente'                                    # slug do agente (nome da pasta em agentes/)
FLOW = os.path.join(RAIZ, 'agentes', SLUG, SLUG + '.json')
SAIDA = os.path.join(RAIZ, 'agentes', SLUG, 'modelos')

# 1) Entradas fictícias do node que monta as mensagens: leia o código dele e monte só os campos que ele usa.
vendedor = {'nome': 'Maria Exemplo', 'email': 'maria.exemplo@empresa.exemplo.com.br', 'telefone': '5511900000001',
            'clientes': [{'Cliente': 'Mercadinho Exemplo', 'Telefone': '(11) 90000-0001', 'Dias sem comprar': 45}]}
saida = rodar_node(FLOW, 'Montar Mensagens do Vendedor', {
    'node': {'Processar Dados': {'data': '19/10/2026', 'vendedores': [vendedor]}, 'Cada Vendedor': vendedor},
    'hoje': '2026-10-19'})[0]

# 2) Peças. E-mail = o HTML do node, sem mexer.
gravar(SAIDA, 'email-vendedor.html', saida['corpo_email'])
url_planilha = 'https://docs.google.com/spreadsheets/d/exemplo-maria-exemplo'
gravar(SAIDA, 'whatsapp-vendedor.html', pagina_whatsapp(
    [dict(texto=saida['mensagem_whatsapp'], link=dict(titulo='Planilha - Maria Exemplo - 19-10-2026', host='docs.google.com',
                                                       href='planilhas/maria-exemplo.html'))],
    'Empresa Exemplo · Comercial', '07:00', 'SEGUNDA-FEIRA', {url_planilha: 'planilhas/maria-exemplo.html'}, 'WhatsApp do vendedor'))
gravar(SAIDA, 'planilhas/maria-exemplo.html', pagina_planilha(
    'Planilha - Maria Exemplo - 19-10-2026', ['Cliente', 'Telefone', 'Dias sem comprar'],
    [['Mercadinho Exemplo', '(11) 90000-0001', 45]], 'Página1', [260, 170, 140]))
# Documento (PDF): imprima o HTML do documento com o navegador sem janela (ver PADRAO.md) para documento/<nome>.pdf.

# 3) modelos.json: a ordem é a do portal.
salvar_manifesto(SAIDA, [
    dict(arquivo='whatsapp-vendedor.html', tipo='whatsapp', rotulo='WhatsApp do vendedor', contato='Empresa Exemplo · Comercial',
         data='SEGUNDA-FEIRA', quem='Cada vendedor'),
    dict(arquivo='email-vendedor.html', tipo='email', rotulo='E-mail do vendedor', assunto=saida['assunto_email'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Maria Exemplo <maria.exemplo@empresa.exemplo.com.br>',
         data='seg., 19 out. 07:00', quem='Cada vendedor com e-mail'),
    dict(arquivo='planilhas/maria-exemplo.html', tipo='planilha', rotulo='Planilha de Maria Exemplo'),
])
print('Modelos de %s gerados em %s' % (SLUG, SAIDA))
