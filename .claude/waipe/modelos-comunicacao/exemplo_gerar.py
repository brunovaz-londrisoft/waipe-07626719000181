# -*- coding: utf-8 -*-
"""Exemplo mínimo de gerador dos modelos de comunicação de um agente. COPIE para a pasta temporária (scratchpad), ADAPTE
e rode de lá. Nunca rode o código dos nodes do flow: leia o código, entenda o texto/HTML que ele monta e reproduza aqui
com dados fictícios.

    python3 exemplo_gerar.py <pasta do repositório>        (ex.: python3 exemplo_gerar.py .)

Cria agentes/modelos/<SLUG>/ e acrescenta o cartão do fluxo em agentes/modelos/index.html (sem recriar o que já existe)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from comum import (pagina_whatsapp, pagina_email, pagina_planilha, card, atualizar_indice)

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '.'
SLUG = 'meu-agente'                        # slug do agente (nome da pasta em agentes/)
NOME = 'Meu Agente'                        # nome legível
MODELOS = os.path.join(RAIZ, 'agentes', 'modelos')
SAIDA = os.path.join(MODELOS, SLUG)

def grava(rel, conteudo):
    caminho = os.path.join(SAIDA, rel)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    open(caminho, 'w', encoding='utf-8').write(conteudo)

# 1) WhatsApp (só se o flow envia WhatsApp). O texto é o MESMO que o node monta (*negrito*, _itálico_, quebras de linha).
texto = 'Olá, Maria Exemplo! Tenha um ótimo dia.\nSegue o seu *resumo* de hoje:\n- Item fictício 1\n- Item fictício 2\n_Mensagem automática do sistema comercial EMPRESA EXEMPLO._'
grava('whatsapp-vendedor.html', pagina_whatsapp(
    NOME + ' · WhatsApp', 'WhatsApp enviado ao vendedor', NOME, 'O que o vendedor recebe no WhatsApp.',
    [('🕖', 'Frequência', 'Toda segunda, 07:00'), ('📲', 'Canal', 'WhatsApp (Z-API oficial)')],
    [dict(texto=texto)], '07:00', 'SEGUNDA-FEIRA', 'Empresa Exemplo · Comercial', '../index.html'))
# Com documento anexado: [dict(texto=texto, doc=dict(nome='Relatorio.pdf', meta='PDF · 1 página(s) · 70 KB'))] e doc=dict(nome=..., href='documento/Relatorio.pdf')
# Com link de planilha: [dict(texto=texto, link=dict(titulo='Planilha ...', host='docs.google.com', href='planilhas/maria-exemplo.html'))] e links={url_visivel: 'planilhas/maria-exemplo.html'}

# 2) E-mail (HTML fragmento IGUAL ao que o node monta, com dados fictícios). celular=True mostra o botão Computador/Celular.
html_email = '<table role="presentation" width="100%"><tr><td style="padding:24px;font-family:Arial">Olá, <b>Maria Exemplo</b>. Conteúdo do e-mail aqui.</td></tr></table>'
grava('email-vendedor.html', pagina_email(
    NOME + ' · E-mail', 'E-mail enviado ao vendedor', NOME, 'O que o vendedor recebe por e-mail.',
    [('🕖', 'Frequência', 'Toda segunda, 07:00'), ('✉️', 'Canal', 'E-mail do cadastro do vendedor')],
    'Assunto do e-mail - EMPRESA EXEMPLO', 'Empresa Exemplo Comercial', 'relatorios@empresa.exemplo.com.br',
    'Maria Exemplo <maria.exemplo@empresa.exemplo.com.br>', 'seg., 19 out. 07:00', html_email, '../index.html'))

# 3) Consolidado do gestor (se o flow envia um): mesma ideia, destinatário = gestor fictício.
# 4) Documento (PDF): imprima o HTML do documento com o navegador sem janela (ver PADRAO.md) para documento/<nome>.pdf.
# 5) Planilhas (se o flow cria planilhas): uma página por vendedor.
grava('planilhas/maria-exemplo.html', pagina_planilha(
    'Planilha - Maria Exemplo - 19-10-2026', ['Cliente', 'Telefone', 'E-mail'],
    [('Mercadinho Exemplo', '(11) 90000-0001', 'contato@mercadinho.exemplo.com.br')], '../whatsapp-vendedor.html', larguras=[260, 170, 280]))

# 6) Índice: SÓ acrescenta (ou troca) o cartão deste fluxo; os outros fluxos não são tocados.
atualizar_indice(MODELOS, card(
    NOME, '🧩', 'Toda segunda, 07:00', 'Cada vendedor', 'Uma linha dizendo o que o fluxo envia.', SLUG,
    [('📲', 'WhatsApp do vendedor', 'whatsapp-vendedor.html'), ('✉️', 'E-mail do vendedor', 'email-vendedor.html'),
     ('📊', 'Planilha de um vendedor', 'planilhas/maria-exemplo.html')]), SLUG)
print('Modelos de %s gerados em %s' % (SLUG, SAIDA))
