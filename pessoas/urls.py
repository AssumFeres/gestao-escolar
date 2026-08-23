from django.urls import path
from .views import ListaPessoasView, DetalhePessoaView

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
    path('<int:pk>/', DetalhePessoaView.as_view(), name='detalhe-pessoa'),
]
