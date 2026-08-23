from django.urls import path
from .views import BuscarCepView, AssociarHabilitacaoView, CadastrarPessoaView

urlpatterns = [
    path('cep/<str:cep>/', BuscarCepView.as_view(), name='api-buscar-cep'),
    path('funcoes-gestao/habilitacoes/', AssociarHabilitacaoView.as_view(), name='api-associar-habilitacao'),
    path('pessoas/', CadastrarPessoaView.as_view(), name='api-cadastrar-pessoa'),
]