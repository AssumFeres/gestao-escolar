from django.urls import path
from .views import BuscarCepView, CadastrarPessoaView, BuscarPessoaPorCpfView

urlpatterns = [
    path('cep/<str:cep>/', BuscarCepView.as_view(), name='api-buscar-cep'),
    path('pessoas/', CadastrarPessoaView.as_view(), name='api-cadastrar-pessoa'),
    path('pessoa-por-cpf/<str:cpf>/', BuscarPessoaPorCpfView.as_view(), name='api-buscar-pessoa-por-cpf'),
]
