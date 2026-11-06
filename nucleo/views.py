from django.views.generic import TemplateView

class HomeView(TemplateView):
    """View da página inicial do sistema."""
    template_name = 'nucleo/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Imports locais à prova de falhas circulares e NameError
        from cadastros.models import AtribuicaoFuncao
        from django.db.models import Q
        
        # CORREÇÃO: Adicionado '__nome' para buscar o texto dentro do relacionamento de Função
        context['instrutores'] = AtribuicaoFuncao.objects.select_related('pessoa').exclude(
            Q(funcao__nome__icontains='aluno') | 
            Q(funcao__nome__icontains='discente')
        ).order_by('pessoa__nome_completo')
        
        return context



class EmConstrucaoView(TemplateView):
    """View provisória para páginas e relatórios em desenvolvimento."""
    template_name = 'nucleo/em_construcao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Imports locais idênticos para garantir que o menu lateral não quebre nesta tela
        from cadastros.models import AtribuicaoFuncao
        from django.db.models import Q
        
        # Saneamento completo do menu lateral dinâmico
        context['instrutores'] = AtribuicaoFuncao.objects.select_related('pessoa').exclude(
            Q(cargo__icontains='aluno') | 
            Q(cargo__icontains='discente')
        ).order_by('pessoa__nome_completo')
        
        # Captura o parâmetro da URL de forma segura
        context['chave'] = self.kwargs.get('chave')
        
        return context
