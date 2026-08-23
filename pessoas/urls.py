from django.urls import path
from .views import ListaPessoasView

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
]

