from django.urls import path
from .views import (
    ListaPessoasView, DetalhePessoaView, NovoCadastroPessoaView,
    EditarPessoaView,
    AdicionarFormacaoDocenteView, EditarFormacaoDocenteView,
    ExcluirFormacaoDocenteView,
    AdicionarHistoricoVinculoFormalView, EncerrarHistoricoVinculoFormalView,
    AdicionarExperienciaProfissionalView, EditarExperienciaProfissionalView,
    ExcluirExperienciaProfissionalView, AdicionarPendenciaCadastroView,
    EditarPendenciaCadastroView, ExcluirPendenciaCadastroView,
    EditarRequisitoContratacaoView,
    ListaDisciplinasView, DetalheDisciplinaView, AdicionarDisciplinaView,
    EditarDisciplinaView, ToggleAtivoDisciplinaView,
    AdicionarConteudoProgramaticoView, EditarConteudoProgramaticoView,
    ToggleAtivoConteudoProgramaticoView,
    ListaSubModulosView, DetalheSubModuloView, AdicionarSubModuloView,
    EditarSubModuloView, ToggleAtivoSubModuloView,
    AdicionarSubModuloDisciplinaView, ExcluirSubModuloDisciplinaView,
    ListaModulosView, DetalheModuloView, AdicionarModuloView,
    EditarModuloView, ToggleAtivoModuloView,
    AdicionarModuloSubModuloView, ExcluirModuloSubModuloView,
    ListaOfertaModulosView, DetalheOfertaModuloView, AdicionarOfertaModuloView,
    EditarOfertaModuloView, EncerrarOfertaModuloView,
    AdicionarTurmaView, EditarTurmaView, ListaTurmasView,
    ListaAtasView, DetalheAtaView, AdicionarAtaView, EditarAtaView,
    AdicionarAtaPessoaView, ExcluirAtaPessoaView,
)

urlpatterns = [
    path('', ListaPessoasView.as_view(), name='lista-pessoas'),
    path('novo/', NovoCadastroPessoaView.as_view(), name='novo-cadastro-pessoa'),
    path('docente/<int:pk>/formacoes/nova/', AdicionarFormacaoDocenteView.as_view(), name='adicionar-formacao-docente'),
    path('formacoes/<int:pk>/editar/', EditarFormacaoDocenteView.as_view(), name='editar-formacao-docente'),
    path('formacoes/<int:pk>/excluir/', ExcluirFormacaoDocenteView.as_view(), name='excluir-formacao-docente'),
    path('atribuicao/<int:pk>/historico-vinculo/novo/', AdicionarHistoricoVinculoFormalView.as_view(), name='adicionar-historico-vinculo'),
    path('historico-vinculo/<int:pk>/encerrar/', EncerrarHistoricoVinculoFormalView.as_view(), name='encerrar-historico-vinculo'),
    path('atribuicao/<int:pk>/experiencias/nova/', AdicionarExperienciaProfissionalView.as_view(), name='adicionar-experiencia'),
    path('experiencias/<int:pk>/editar/', EditarExperienciaProfissionalView.as_view(), name='editar-experiencia'),
    path('experiencias/<int:pk>/excluir/', ExcluirExperienciaProfissionalView.as_view(), name='excluir-experiencia'),
    path('atribuicao/<int:pk>/pendencias/nova/', AdicionarPendenciaCadastroView.as_view(), name='adicionar-pendencia'),
    path('pendencias/<int:pk>/editar/', EditarPendenciaCadastroView.as_view(), name='editar-pendencia'),
    path('pendencias/<int:pk>/excluir/', ExcluirPendenciaCadastroView.as_view(), name='excluir-pendencia'),
    path('atribuicao/<int:pk>/requisito-contratacao/editar/', EditarRequisitoContratacaoView.as_view(), name='editar-requisito-contratacao'),

    # Disciplina + ConteudoProgramatico (estrutura curricular, docs/33) — CRU, sem Delete.
    # Colocadas ANTES de '<int:pk>/' para não colidir com a rota de detalhe de Pessoa.
    path('disciplinas/', ListaDisciplinasView.as_view(), name='lista-disciplinas'),
    path('disciplinas/nova/', AdicionarDisciplinaView.as_view(), name='adicionar-disciplina'),
    path('disciplinas/<int:pk>/', DetalheDisciplinaView.as_view(), name='detalhe-disciplina'),
    path('disciplinas/<int:pk>/editar/', EditarDisciplinaView.as_view(), name='editar-disciplina'),
    path('disciplinas/<int:pk>/toggle-ativo/', ToggleAtivoDisciplinaView.as_view(), name='toggle-ativo-disciplina'),
    path('disciplinas/<int:pk>/conteudo-programatico/novo/', AdicionarConteudoProgramaticoView.as_view(), name='adicionar-conteudo-programatico'),
    path('conteudo-programatico/<int:pk>/editar/', EditarConteudoProgramaticoView.as_view(), name='editar-conteudo-programatico'),
    path('conteudo-programatico/<int:pk>/toggle-ativo/', ToggleAtivoConteudoProgramaticoView.as_view(), name='toggle-ativo-conteudo-programatico'),

    # SubModulo + SubModuloDisciplina (estrutura curricular, docs/33/docs/34) — SubModulo é CRU;
    # o vínculo com Disciplina permite Delete real (desvincular, não perde rastreabilidade).
    path('submodulos/', ListaSubModulosView.as_view(), name='lista-submodulos'),
    path('submodulos/novo/', AdicionarSubModuloView.as_view(), name='adicionar-submodulo'),
    path('submodulos/<int:pk>/', DetalheSubModuloView.as_view(), name='detalhe-submodulo'),
    path('submodulos/<int:pk>/editar/', EditarSubModuloView.as_view(), name='editar-submodulo'),
    path('submodulos/<int:pk>/toggle-ativo/', ToggleAtivoSubModuloView.as_view(), name='toggle-ativo-submodulo'),
    path('submodulos/<int:pk>/disciplinas/nova/', AdicionarSubModuloDisciplinaView.as_view(), name='adicionar-submodulo-disciplina'),
    path('submodulo-disciplina/<int:pk>/excluir/', ExcluirSubModuloDisciplinaView.as_view(), name='excluir-submodulo-disciplina'),

    # Modulo + ModuloSubModulo (estrutura curricular, docs/33/docs/34) — mesmo padrão de SubModulo.
    path('modulos/', ListaModulosView.as_view(), name='lista-modulos'),
    path('modulos/novo/', AdicionarModuloView.as_view(), name='adicionar-modulo'),
    path('modulos/<int:pk>/', DetalheModuloView.as_view(), name='detalhe-modulo'),
    path('modulos/<int:pk>/editar/', EditarModuloView.as_view(), name='editar-modulo'),
    path('modulos/<int:pk>/toggle-ativo/', ToggleAtivoModuloView.as_view(), name='toggle-ativo-modulo'),
    path('modulos/<int:pk>/submodulos/novo/', AdicionarModuloSubModuloView.as_view(), name='adicionar-modulo-submodulo'),
    path('modulo-submodulo/<int:pk>/excluir/', ExcluirModuloSubModuloView.as_view(), name='excluir-modulo-submodulo'),

    # OfertaModulo + Turma (estrutura curricular, docs/33/docs/35).
    path('ofertas-modulo/', ListaOfertaModulosView.as_view(), name='lista-ofertas-modulo'),
    path('ofertas-modulo/nova/', AdicionarOfertaModuloView.as_view(), name='adicionar-oferta-modulo'),
    path('ofertas-modulo/<int:pk>/', DetalheOfertaModuloView.as_view(), name='detalhe-oferta-modulo'),
    path('ofertas-modulo/<int:pk>/editar/', EditarOfertaModuloView.as_view(), name='editar-oferta-modulo'),
    path('ofertas-modulo/<int:pk>/encerrar/', EncerrarOfertaModuloView.as_view(), name='encerrar-oferta-modulo'),
    path('ofertas-modulo/<int:pk>/turmas/nova/', AdicionarTurmaView.as_view(), name='adicionar-turma'),
    path('turmas/', ListaTurmasView.as_view(), name='lista-turmas'),
    path('turmas/<int:pk>/editar/', EditarTurmaView.as_view(), name='editar-turma'),

    # Ata + AtaPessoa (estrutura curricular, docs/33/docs/35) — AtaPessoa é
    # exceção provisória, migra para o módulo Atribuição no futuro.
    path('atas/', ListaAtasView.as_view(), name='lista-atas'),
    path('atas/nova/', AdicionarAtaView.as_view(), name='adicionar-ata'),
    path('atas/<int:pk>/', DetalheAtaView.as_view(), name='detalhe-ata'),
    path('atas/<int:pk>/editar/', EditarAtaView.as_view(), name='editar-ata'),
    path('atas/<int:pk>/pessoas/nova/', AdicionarAtaPessoaView.as_view(), name='adicionar-ata-pessoa'),
    path('ata-pessoa/<int:pk>/excluir/', ExcluirAtaPessoaView.as_view(), name='excluir-ata-pessoa'),

    path('<int:pk>/editar/', EditarPessoaView.as_view(), name='editar-pessoa'),
    path('<int:pk>/', DetalhePessoaView.as_view(), name='detalhe-pessoa'),
]
