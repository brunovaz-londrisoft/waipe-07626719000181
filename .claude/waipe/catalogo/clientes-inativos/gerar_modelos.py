# -*- coding: utf-8 -*-
"""Modelos de comunicação do Agente de Clientes Inativos: roda os nodes reais com dados fictícios (nada é enviado).
Rode: python3 gerar_modelos.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'modelos-comunicacao'))
from comum import modelo_do_arquivo, gravar, rodar_node, salvar_manifesto

SLUG, FLOW, SAIDA = modelo_do_arquivo(__file__)
HOJE = '2026-10-01'
# Clientes fictícios: nome, e-mail, última compra
CLIENTES = [('Roberto Lima', 'roberto.lima@exemplo.com.br', '2026-06-12'), ('Elétrica Silva & Filhos', 'eletrica.silva.filhos@exemplo.com.br', '2026-05-26'),
            ('Marcenaria Bom Jardim', 'marcenaria.bom.jardim@exemplo.com.br', '2026-05-17'), ('Construtora Horizonte', 'construtora.horizonte@exemplo.com.br', '2026-05-15'),
            ('Ana Paula Ferreira', 'ana.paula.ferreira@exemplo.com.br', '2026-05-01'), ('Instalações Raio Azul', 'instalacoes.raio.azul@exemplo.com.br', '2026-03-17'),
            ('Casa Verde Reformas', 'casa.verde.reformas@exemplo.com.br', '2026-03-03'), ('Gabriel Santana', 'gabriel.santana@exemplo.com.br', '2026-03-01'),
            ('Eletro Norte Serviços', 'eletro.norte.servicos@exemplo.com.br', '2026-01-29'), ('Padaria Pão Dourado', 'padaria.pao.dourado@exemplo.com.br', '2026-01-03'),
            ('Clínica Vida Plena', 'clinica.vida.plena@exemplo.com.br', '2025-10-27'), ('Marina Costa Arquitetura', 'marina.costa.arquitetura@exemplo.com.br', '2025-10-10')]

registros = [dict(codigo=str(3000 + i), nome=n, email=e, celular='', fone='', dtultimacompra=d) for i, (n, e, d) in enumerate(CLIENTES)]
# Fora da janela de 90 a 365 dias ou ignorados: mostram que o filtro funciona
registros += [dict(codigo='3990', nome='Cliente Recente Exemplo', email='recente@exemplo.com.br', celular='', fone='', dtultimacompra='2026-09-20'),
              dict(codigo='3991', nome='CONSUMIDOR FINAL', email='', celular='', fone='', dtultimacompra='2026-05-01')]
filtro = rodar_node(FLOW, 'Filtrar Inativos 90 a 365 dias',
                    {'items': [{'json': {'dados': [{'dados': registros, 'erros': [], 'totalRegistros': len(registros)}]}}], 'hoje': HOJE})[0]
resumo = rodar_node(FLOW, 'Montar Resumo', {'items': [{'json': {}}], 'node': {'Filtrar Inativos 90 a 365 dias': filtro}, 'hoje': HOJE})[0]
primeiro = sorted(filtro['clientes_email'], key=lambda c: c['dias_sem_comprar'])[0]
gravar(SAIDA, 'email-cliente.html', primeiro['email_html'])
gravar(SAIDA, 'consolidado-gestor.html', resumo['resumo_html'])

salvar_manifesto(SAIDA, [
    dict(arquivo='email-cliente.html', tipo='email', rotulo='E-mail ao cliente', assunto=primeiro['email_assunto'],
         de='Empresa Exemplo <vendas@empresa.exemplo.com.br>', para='%s <%s>' % (primeiro['nome_saudacao'], primeiro['email']),
         data='qui., 1 out. 08:00', quem='Cada cliente inativo com e-mail'),
    dict(arquivo='consolidado-gestor.html', tipo='email', rotulo='Resumo do gestor', assunto=resumo['resumo_assunto'],
         de='Relatórios Waipe <relatorios@empresa.exemplo.com.br>', para='Nome do Gestor <gestor@empresa.exemplo.com.br>',
         data='qui., 1 out. 08:12', quem='Gestor'),
])
