"""
nucleo/context_processors.py

Injeta MENU_NAVEGACAO em todo template automaticamente (via TEMPLATES em
config/settings.py). Também calcula, a partir da URL atual
(request.resolver_match), qual item do menu está "ativo" e qual grupo deve
aparecer aberto.

Correção de 07/09/2026: itens sem tela própria (url_name=None) são
identificados pela 'chave' (única no sistema), não mais pelo 'label' — três
itens diferentes podem ter o mesmo texto visível ("Relatórios" aparece em 3
grupos), e usar o texto como identidade fazia os três acenderem juntos.
"""

from .menu import MENU_NAVEGACAO


def menu_navegacao(request):
    match = getattr(request, 'resolver_match', None)
    url_name_atual = match.url_name if match else None

    chave_em_construcao = None
    if url_name_atual == 'em-construcao' and match.kwargs:
        chave_em_construcao = match.kwargs.get('chave')

    menu = []
    for grupo in MENU_NAVEGACAO:
        itens_calculados = []
        grupo_aberto = False

        for item in grupo['itens']:
            if item.get('url_name'):
                nomes_ativos = item.get('url_names_ativos', [item['url_name']])
                ativo = url_name_atual in nomes_ativos
            else:
                ativo = chave_em_construcao == item.get('chave')

            item_calculado = dict(item)
            item_calculado['ativo'] = ativo
            itens_calculados.append(item_calculado)

            if ativo:
                grupo_aberto = True

        menu.append({
            'grupo': grupo['grupo'],
            'itens': itens_calculados,
            'aberto': grupo_aberto,
        })

    return {'MENU_NAVEGACAO': menu}
