from django.urls import path
from .views import (
    GerenciarTurmaView, AdicionarMatriculaTurmaView, EditarMatriculaTurmaView,
    ExcluirMatriculaTurmaView, FinalizarPlanejamentoView,
)

urlpatterns = [
    path('turmas/<int:pk>/', GerenciarTurmaView.as_view(), name='gerenciar-turma'),
    path('turmas/<int:pk>/alunos/novo/', AdicionarMatriculaTurmaView.as_view(), name='adicionar-matricula-turma'),
    path('matriculas/<int:pk>/editar/', EditarMatriculaTurmaView.as_view(), name='editar-matricula-turma'),
    path('matriculas/<int:pk>/excluir/', ExcluirMatriculaTurmaView.as_view(), name='excluir-matricula-turma'),
    path('turmas/<int:pk>/finalizar-planejamento/', FinalizarPlanejamentoView.as_view(), name='finalizar-planejamento'),
]
