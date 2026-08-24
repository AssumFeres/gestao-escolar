from django.urls import path
from .views import ListaPessoasView, DetalhePessoaView, NovoCadastroPessoaView

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
    path('novo/', NovoCadastroPessoaView.as_view(), name='novo-cadastro-pessoa'),
    path('<int:pk>/', DetalhePessoaView.as_view(), name='detalhe-pessoa'),
]
