"""
nucleo/views.py

HomeView          — tela inicial da navegação.
EmConstrucaoView  — placeholder para qualquer módulo do menu que ainda não
                    tem tela própria. Recebe a 'chave' (identificador único,
                    ver menu.py) pela URL, e resolve o texto (label) a
                    exibir procurando essa chave em MENU_NAVEGACAO — assim
                    o texto mostrado na tela sempre bate com o que aparece
                    no menu, sem duplicar a lista de nomes aqui.
"""

from django.views.generic import TemplateView

from .menu import MENU_NAVEGACAO

# Rótulos para chaves que não vêm de MENU_NAVEGACAO (hoje, só o logout do
# cabeçalho, que não é um item de menu de verdade).
_ROTULOS_EXTRAS = {
    'logout': 'Logout',
}


def _rotulo_por_chave(chave):
    for grupo in MENU_NAVEGACAO:
        for item in grupo['itens']:
            if item.get('chave') == chave:
                return item['label']
    return _ROTULOS_EXTRAS.get(chave, chave)


class HomeView(TemplateView):
    template_name = 'nucleo/home.html'


class EmConstrucaoView(TemplateView):
    template_name = 'nucleo/em_construcao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulo'] = _rotulo_por_chave(kwargs.get('chave', ''))
        return context
