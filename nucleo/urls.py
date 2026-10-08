from django.urls import path
from .views import HomeView, EmConstrucaoView
from atribuicao import views as atribuicao_views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    # Mudamos para usar a EmConstrucaoView.as_view() e passamos a chave no contexto
    path('em-construcao/registro-instrucao/', EmConstrucaoView.as_view(), {'chave': 'registro_instrucao'}, name='registro_instrucao'),
    path('em-construcao/<str:chave>/', EmConstrucaoView.as_view(), name='em-construcao'),
]
