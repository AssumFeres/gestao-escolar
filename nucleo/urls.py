from django.urls import path
from .views import HomeView, EmConstrucaoView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('em-construcao/<str:chave>/', EmConstrucaoView.as_view(), name='em-construcao'),
]
