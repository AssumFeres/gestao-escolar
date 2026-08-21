from django.urls import path
from .views import BuscarCepView

urlpatterns = [
    path('cep/<str:cep>/', BuscarCepView.as_view(), name='api-buscar-cep'),
]

