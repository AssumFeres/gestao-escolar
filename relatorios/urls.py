from django.urls import path
from .views import CentralRelatoriosView, ExportarRelatorioPDFView

# O Django exige estritamente que este arquivo tenha APENAS a lista 'urlpatterns'
urlpatterns = [
    path('central/', CentralRelatoriosView.as_view(), name='central_relatorios'),
    path('central/exportar-pdf/', ExportarRelatorioPDFView.as_view(), name='exportar_pdf'),
]
