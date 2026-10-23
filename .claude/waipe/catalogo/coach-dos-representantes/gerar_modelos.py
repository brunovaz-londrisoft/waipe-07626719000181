# -*- coding: utf-8 -*-
"""Modelos de comunicação do Coach dos Representantes: roda os nodes reais com dados fictícios (nada é enviado).
O PDF de exemplo (modelos/documento/) é mantido como está. Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, pagina_whatsapp, gravar, rodar_node, salvar_manifesto, slug_de

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)

# Carteira fictícia da Helena Prado: código, cliente, última compra, dias sem comprar
HELENA = [('10231', 'Casa de Doces Aurora', '19/03/2026', 214), ('10238', 'Confeitaria Ouro Verde', '15/04/2026', 187),
          ('10245', 'Confeitaria Nova Era', '09/05/2026', 163), ('10252', 'Doceria Beira Rio', '31/05/2026', 141),
          ('10259', 'Sacolão Ouro Verde', '23/06/2026', 118), ('10266', 'Panificadora Estrela', '15/07/2026', 96),
          ('10273', 'Panificadora Tio Zé', '23/07/2026', 88), ('10280', 'Mercadinho Bom Preço', '06/08/2026', 74),
          ('10287', 'Minimercado Beira Rio', '19/08/2026', 61), ('10294', 'Minimercado Pão Dourado', '28/08/2026', 52),
          ('10301', 'Minimercado Raio de Sol', '02/09/2026', 47), ('10308', 'Cafeteria Vila Verde', '10/09/2026', 39),
          ('10315', 'Bomboniere Beira Rio', '16/09/2026', 33), ('10322', 'Lanchonete Lírio', '21/09/2026', 28)]
# nome, código, faturamento, % da meta, atendidos, pendentes, comissão %
BASE = [('Sabrina Teles', '105', 41600.00, 26.0, 3, 11, 2.5), ('Larissa Nunes', '103', 96100.00, 48.0, 9, 17, 3.0),
        ('Helena Prado', '101', 117432.50, 65.24, 16, 14, 3.0), ('Davi Calheiros', '104', 87640.00, 73.0, 10, 6, 3.0),
        ('Otávio Brandão', '102', 162300.00, 108.2, 22, 7, 3.5)]
LOJAS = ['Mercearia', 'Panificadora', 'Doceria', 'Confeitaria', 'Minimercado', 'Cafeteria', 'Bomboniere', 'Lanchonete']
SUFIXOS = ['Aurora', 'Bela Vista', 'Beira Rio', 'Primavera', 'Ouro Verde', 'Estrela', 'Lírio', 'Campo Belo', 'Vila Verde', 'Sol Nascente']

vendedores, linhas = [], []
for k, (nome, cod, fat, pct, atend, pend, com) in enumerate(BASE):
    meta = round(fat / pct * 100 / 1000) * 1000
    if nome == 'Helena Prado':
        cli = [dict(codigo=c, nome=n, dataUltimaCompra=dt, diasSemComprar=str(d), diasOrdenacao=d) for c, n, dt, d in HELENA]
    else:
        cli = []
        for i in range(pend):
            dias = 210 - i * 13 - k * 3
            cli.append(dict(codigo=str(20000 + k * 100 + i), nome='%s %s' % (LOJAS[(i + k) % 8], SUFIXOS[(i * 3 + k) % 10]),
                            dataUltimaCompra='%02d/%02d/2026' % (1 + (i * 7) % 27, max(1, 10 - dias // 30)), diasSemComprar=str(dias), diasOrdenacao=dias))
    pct_real = fat / meta * 100
    vendedores.append(dict(codigo=cod, nome=nome, email=slug_de(nome).replace('-', '.') + '@empresa.exemplo.com.br', telefone='5511900000%03d' % int(cod),
                           faturamento_atual=fat, meta=meta, percentual_atingimento=pct_real, qtd_atendidos=atend, qtd_pendentes=len(cli),
                           comissao_percentual=com, comissao_valor=fat * com / 100, comissao_cadastrada=True, clientes_pendentes=cli))
    linhas.append(dict(grupo=cod, nome=nome, faturamentoAtual=fat, meta=meta, percentual=pct_real, qtdAtendidos=atend, qtdPendentes=len(cli),
                       comissaoValor=fat * com / 100, comissaoPercentual=com, comissaoCadastrada=True))
fat_t, meta_t = sum(v['faturamento_atual'] for v in vendedores), sum(v['meta'] for v in vendedores)
processado = dict(gerado_em='2026-10-19T10:00:00.000Z', vendedores=vendedores, relatorio_gestor=dict(
    email_gestor='gestor@empresa.exemplo.com.br', assunto='Relatório Consolidado Semanal - Coach de Vendas NOME DA EMPRESA', nome_gestor='Nome do Gestor',
    faturamento_total_empresa=fat_t, meta_total_empresa=meta_t, percentual_atingimento_global=fat_t / meta_t * 100,
    comissao_total_empresa=sum(v['comissao_valor'] for v in vendedores),
    vendedores_sem_email=[dict(nome='Davi Calheiros', codigo='104', motivo='sem e-mail cadastrado')],
    vendedores_sem_telefone=[dict(nome='Sabrina Teles', codigo='105', motivo='número inválido: 119999')],
    grupos_sem_atividade_ocultos=2, vendedores_fora_da_planilha=['Vendedor Exemplo'], qtd_vendedores_fora_da_planilha=1,
    linhas_resumo=sorted(linhas, key=lambda l: l['percentual'])))

helena = next(v for v in vendedores if v['nome'] == 'Helena Prado')
vend = rodar_node(FLOW, 'Montar Mensagens do Vendedor', {'json': helena})[0]
ges = rodar_node(FLOW, 'Montar E-mail do Gestor', {'node': {'Processar Carteiras': processado}})[0]
gravar(SAIDA, 'email-vendedor.html', vend['corpo_email_resumo'])
gravar(SAIDA, 'consolidado-gestor.html', ges['corpo_html'])
pdf = 'documento/Relatorio-Helena-Prado.pdf'
kb = os.path.getsize(os.path.join(SAIDA, pdf)) // 1024
gravar(SAIDA, 'whatsapp-vendedor.html', pagina_whatsapp(
    [dict(texto=vend['mensagem_whatsapp'], doc=dict(nome='Relatorio-Helena-Prado.pdf', meta='PDF · 1 página · %d KB' % kb, href=pdf))],
    'Empresa Exemplo · Comercial', '07:00', 'SEGUNDA-FEIRA', None, 'WhatsApp do vendedor'))

DE = 'Relatórios Waipe <relatorios@empresa.exemplo.com.br>'
salvar_manifesto(SAIDA, [
    dict(arquivo='whatsapp-vendedor.html', tipo='whatsapp', rotulo='WhatsApp do vendedor', contato='Empresa Exemplo · Comercial',
         data='SEGUNDA-FEIRA', quem='Cada vendedor'),
    dict(arquivo='email-vendedor.html', tipo='email', rotulo='E-mail do vendedor', assunto='Seu resumo semanal - Coach de Vendas NOME DA EMPRESA',
         de=DE, para='Helena Prado <%s>' % helena['email'], data='seg., 19 out. 07:00', quem='Cada vendedor com e-mail'),
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='Consolidado do gestor', assunto=ges['assunto'], de=DE,
         para='Nome do Gestor <gestor@empresa.exemplo.com.br>', data='seg., 19 out. 07:08', quem='Gestor comercial'),
    dict(arquivo=pdf, tipo='documento', rotulo='Relatório em PDF do vendedor', quem='Cada vendedor (anexo do WhatsApp)'),
])
