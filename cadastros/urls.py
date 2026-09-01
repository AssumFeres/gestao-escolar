from django.urls import path
from .views import (
    ListaPessoasView, DetalhePessoaView, NovoCadastroPessoaView,
    PreencherRequisitosDocenteView, AdicionarFormacaoDocenteView,
)

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
    path('novo/', NovoCadastroPessoaView.as_view(), name='novo-cadastro-pessoa'),
    path('docente/<int:pk>/requisitos/', PreencherRequisitosDocenteView.as_view(), name='preencher-requisitos-docente'),
    path('docente/<int:pk>/formacoes/nova/', AdicionarFormacaoDocenteView.as_view(), name='adicionar-formacao-docente'),
    path('<int:pk>/', DetalhePessoaView.as_view(), name='detalhe-pessoa'),
]
