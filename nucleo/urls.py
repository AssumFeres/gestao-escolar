from django.urls import path, include
from .views import HomeView, EmConstrucaoView
from atribuicao import views as atribuicao_views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('atribuicao/', include('atribuicao.urls')),
    path('em-construcao/<str:chave>/', EmConstrucaoView.as_view(), name='em-construcao'),
]
