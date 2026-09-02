from django.urls import path
from .views import (
    ListaPessoasView, DetalhePessoaView, NovoCadastroPessoaView,
    PreencherRequisitosDocenteView, AdicionarFormacaoDocenteView,
    EditarFormacaoDocenteView, AdicionarHistoricoVinculoFormalView,
    EncerrarHistoricoVinculoFormalView,
)

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
    path('novo/', NovoCadastroPessoaView.as_view(), name='novo-cadastro-pessoa'),
    path('docente/<int:pk>/requisitos/', PreencherRequisitosDocenteView.as_view(), name='preencher-requisitos-docente'),
    path('docente/<int:pk>/formacoes/nova/', AdicionarFormacaoDocenteView.as_view(), name='adicionar-formacao-docente'),
    path('formacoes/<int:pk>/editar/', EditarFormacaoDocenteView.as_view(), name='editar-formacao-docente'),
    path('atribuicao/<int:pk>/historico-vinculo/novo/', AdicionarHistoricoVinculoFormalView.as_view(), name='adicionar-historico-vinculo'),
    path('historico-vinculo/<int:pk>/encerrar/', EncerrarHistoricoVinculoFormalView.as_view(), name='encerrar-historico-vinculo'),
    path('<int:pk>/', DetalhePessoaView.as_view(), name='detalhe-pessoa'),
]
