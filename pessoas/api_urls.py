from django.urls import path
from .views import BuscarCepView, AssociarHabilitacaoView

urlpatterns = [
    path('cep/<str:cep>/', BuscarCepView.as_view(), name='api-buscar-cep'),
    path('funcoes-gestao/habilitacoes/', AssociarHabilitacaoView.as_view(), name='api-associar-habilitacao'),
]
