from django.urls import path
from .views import BuscarCepView, CadastrarPessoaView

urlpatterns = [
    path('cep/<str:cep>/', BuscarCepView.as_view(), name='api-buscar-cep'),
    path('pessoas/', CadastrarPessoaView.as_view(), name='api-cadastrar-pessoa'),
]