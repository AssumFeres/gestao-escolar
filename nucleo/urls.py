from django.urls import path, include
from .views import HomeView, EmConstrucaoView
from atribuicao import views as atribuicao_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('atribuicao/', include('atribuicao.urls')),
    path('em-construcao/<str:chave>/', EmConstrucaoView.as_view(), name='em-construcao'),
    # Rota oficial de login apontando para o arquivo HTML criado
    path('login/', auth_views.LoginView.as_view(template_name='nucleo/login.html'), name='login'),
]
