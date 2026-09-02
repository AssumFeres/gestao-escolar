"""
cadastros/views.py

Views (API e Template): traduzem HTTP <-> Service. Não contêm regra de negócio.
"""
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Pessoa, Funcao, CategoriaFuncao, DadosDocente, FormacaoDocente,
    AtribuicaoFuncao, HistoricoVinculoFormal, ExperienciaProfissional,
    PendenciaCadastro,
)
from .forms import (
    CadastrarPessoaForm, FormacaoDocenteModelForm,
    HistoricoVinculoFormalModelForm, EncerrarHistoricoVinculoFormalForm,
    ExperienciaProfissionalModelForm, PendenciaCadastroModelForm,
    EditarPendenciaCadastroForm, EditarRequisitoContratacaoForm,
    FormacaoDocenteFormSet, ExperienciaProfissionalFormSet,
    HistoricoVinculoFormalFormSet, PendenciaCadastroFormSet,
)
from .services import (
    BuscarEnderecoPorCepService,
    CadastrarPessoaComFuncaoService,
)
from .serializers import (
    BuscarCepInputSerializer, EnderecoOutputSerializer,
    CadastrarPessoaInputSerializer, CadastrarPessoaOutputSerializer,
)


class BuscarCepView(APIView):
    """
    SRP: única responsabilidade é traduzir HTTP <-> BuscarEnderecoPorCepService.
    """

    def get(self, request, cep):
        input_serializer = BuscarCepInputSerializer(data={"cep": cep})
        input_serializer.is_valid(raise_exception=True)

        try:
            endereco = BuscarEnderecoPorCepService().executar(cep)
        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_404_NOT_FOUND)

        output_serializer = EnderecoOutputSerializer(endereco.__dict__)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CadastrarPessoaView(APIView):
    """
    SRP: única responsabilidade é traduzir HTTP <-> CadastrarPessoaComFuncaoService.

    Versão mínima via API: cadastra Pessoa + AtribuicaoFuncao, sem os campos
    repetíveis (Formação/Experiência/Histórico/Pendências) — esses só estão
    disponíveis pelo formulário HTML (NovoCadastroPessoaView) por enquanto.
    """

    def post(self, request):
        input_serializer = CadastrarPessoaInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        dados = input_serializer.validated_data

        dados_pessoa = {
            "nome_completo": dados["nome_completo"],
            "cpf": dados["cpf"],
            "data_nascimento": dados["data_nascimento"],
            "email": dados["email"],
            "telefone": dados["telefone"],
            "endereco_cep": dados["endereco_cep"],
            "endereco_logradouro": dados["endereco_logradouro"],
            "endereco_numero": dados["endereco_numero"],
            "endereco_complemento": dados.get("endereco_complemento", ""),
            "endereco_bairro": dados["endereco_bairro"],
            "endereco_cidade": dados["endereco_cidade"],
            "endereco_uf": dados["endereco_uf"],
        }

        funcao = get_object_or_404(Funcao, pk=dados["funcao_id"])

        dados_atribuicao = {
            "data_inicio": dados["data_inicio"],
            "situacao": dados["situacao"],
        }

        try:
            pessoa, atribuicao, dados_docente = CadastrarPessoaComFuncaoService().executar(
                dados_pessoa=dados_pessoa,
                funcao=funcao,
                dados_atribuicao=dados_atribuicao,
            )
        except ValidationError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = CadastrarPessoaOutputSerializer({
            "pessoa_id": pessoa.id,
            "nome_completo": pessoa.nome_completo,
            "funcao": funcao.nome,
            "atribuicao_id": atribuicao.id,
        })
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ListaPessoasView(ListView):
    """
    Template View: renderiza HTML no servidor, sem passar por Serializer/JSON.
    """
    model = Pessoa
    template_name = 'cadastros/lista.html'
    context_object_name = 'pessoas'


class DetalhePessoaView(DetailView):
    """
    Template View: mostra os dados completos de uma Pessoa e suas Funções.
    """
    model = Pessoa
    template_name = 'cadastros/detalhe.html'
    context_object_name = 'pessoa'


# Campo usado para decidir se uma linha de Formset foi de fato preenchida
# (Formsets sempre entregam a linha `extra`, mesmo vazia — precisa filtrar).
_CAMPO_PREENCHIDO = {
    'formacao': 'curso',
    'experiencia': 'organizacao',
    'historico': 'vinculo_formal',
    'pendencia': 'tipo',
}


def _linhas_preenchidas(cleaned_data_list, campo_chave):
    """Descarta linhas de Formset deixadas em branco (extra=1 sempre entrega 1 linha)."""
    return [linha for linha in cleaned_data_list if linha.get(campo_chave)]


class NovoCadastroPessoaView(View):
    """
    Template View: formulario HTML de cadastro. Reusa o mesmo Service
    da API (CadastrarPessoaComFuncaoService) — mesma regra de negocio,
    caminho de entrada diferente.

    Formulário único com dropdown de Funcao; os Formsets de Formação/
    Experiência/Histórico de Vínculo Formal/Pendências são sempre enviados,
    mas só os relevantes para a categoria escolhida são de fato usados pelo
    Service (Pendências é universal, sempre usada) — o Template/JavaScript
    (Etapa 7.4c/d) é quem decide quais blocos mostrar visualmente, mas o
    back-end aceita o POST completo de qualquer forma.
    """
    template_name = 'cadastros/form_pessoa.html'

    def _formsets(self, dados_post=None):
        return (
            FormacaoDocenteFormSet(dados_post, prefix='formacao'),
            ExperienciaProfissionalFormSet(dados_post, prefix='experiencia'),
            HistoricoVinculoFormalFormSet(dados_post, prefix='historico'),
            PendenciaCadastroFormSet(dados_post, prefix='pendencia'),
        )

    def _funcao_categorias(self):
        """Mapa {id_da_funcao: categoria}, usado pelo JS para saber qual bloco mostrar."""
        return {f.id: f.categoria for f in Funcao.objects.all()}

    def get(self, request):
        form = CadastrarPessoaForm()
        formacao_fs, experiencia_fs, historico_fs, pendencia_fs = self._formsets()
        return render(request, self.template_name, {
            'form': form,
            'formacao_formset': formacao_fs,
            'experiencia_formset': experiencia_fs,
            'historico_formset': historico_fs,
            'pendencia_formset': pendencia_fs,
            'funcao_categorias': self._funcao_categorias(),
        })

    def post(self, request):
        form = CadastrarPessoaForm(request.POST)
        formacao_fs, experiencia_fs, historico_fs, pendencia_fs = self._formsets(request.POST)

        formularios_validos = (
            form.is_valid() and formacao_fs.is_valid()
            and experiencia_fs.is_valid() and historico_fs.is_valid()
            and pendencia_fs.is_valid()
        )
        if not formularios_validos:
            return render(request, self.template_name, {
                'form': form,
                'formacao_formset': formacao_fs,
                'experiencia_formset': experiencia_fs,
                'historico_formset': historico_fs,
                'pendencia_formset': pendencia_fs,
                'funcao_categorias': self._funcao_categorias(),
            })

        dados = form.cleaned_data
        funcao = dados['funcao']

        dados_pessoa = {
            "nome_completo": dados["nome_completo"],
            "cpf": dados["cpf"],
            "data_nascimento": dados["data_nascimento"],
            "email": dados["email"],
            "telefone": dados["telefone"],
            "registro_matricula": dados.get("registro_matricula") or None,
            "registro_aluno": dados.get("registro_aluno") or None,
            "codigo_anac": dados.get("codigo_anac") or None,
            "sexo": dados.get("sexo", ""),
            "identidade": dados.get("identidade", ""),
            "data_emissao_identidade": dados.get("data_emissao_identidade"),
            "orgao_expedidor_identidade": dados.get("orgao_expedidor_identidade", ""),
            "naturalidade": dados.get("naturalidade", ""),
            "uf_naturalidade": dados.get("uf_naturalidade", ""),
            "nacionalidade": dados.get("nacionalidade", ""),
            "filiacao_1": dados.get("filiacao_1", ""),
            "filiacao_2": dados.get("filiacao_2", ""),
            "nivel_instrucao": dados.get("nivel_instrucao", ""),
            "estado_civil": dados.get("estado_civil", ""),
            "raca_cor": dados.get("raca_cor", ""),
            "endereco_cep": dados["endereco_cep"],
            "endereco_logradouro": dados["endereco_logradouro"],
            "endereco_numero": dados["endereco_numero"],
            "endereco_complemento": dados.get("endereco_complemento", ""),
            "endereco_bairro": dados["endereco_bairro"],
            "endereco_cidade": dados["endereco_cidade"],
            "endereco_uf": dados["endereco_uf"],
        }

        dados_atribuicao = {
            "data_inicio": dados["data_inicio"],
            "situacao": dados["situacao"],
        }

        dados_extensao = None
        formacoes = None
        experiencias = None
        historico_vinculo_formal = None

        if funcao.categoria == CategoriaFuncao.DISCENTE:
            dados_extensao = {
                "codigo_matricula_anac": dados.get("codigo_matricula_anac") or None,
                "passaporte": dados.get("passaporte", ""),
                "autorizacao_permanencia": dados.get("autorizacao_permanencia", ""),
                "contato_emergencia_nome": dados.get("contato_emergencia_nome", ""),
                "contato_emergencia_parentesco": dados.get("contato_emergencia_parentesco", ""),
                "contato_emergencia_telefone": dados.get("contato_emergencia_telefone", ""),
                "contato_emergencia_endereco": dados.get("contato_emergencia_endereco", ""),
                "responsavel_nome": dados.get("responsavel_nome", ""),
                "responsavel_endereco": dados.get("responsavel_endereco", ""),
                "responsavel_identidade": dados.get("responsavel_identidade", ""),
                "responsavel_orgao_expedidor": dados.get("responsavel_orgao_expedidor", ""),
                "responsavel_data_emissao": dados.get("responsavel_data_emissao"),
                "responsavel_qualificacao": dados.get("responsavel_qualificacao", ""),
            }

        elif funcao.categoria == CategoriaFuncao.DOCENTE:
            dados_extensao = {}
            formacoes = _linhas_preenchidas(formacao_fs.cleaned_data, _CAMPO_PREENCHIDO['formacao'])
            historico_vinculo_formal = _linhas_preenchidas(
                historico_fs.cleaned_data, _CAMPO_PREENCHIDO['historico']
            )

        elif funcao.categoria == CategoriaFuncao.GESTAO:
            experiencias = _linhas_preenchidas(
                experiencia_fs.cleaned_data, _CAMPO_PREENCHIDO['experiencia']
            )
            historico_vinculo_formal = _linhas_preenchidas(
                historico_fs.cleaned_data, _CAMPO_PREENCHIDO['historico']
            )

        if funcao.categoria in (CategoriaFuncao.DOCENTE, CategoriaFuncao.GESTAO) and not historico_vinculo_formal:
            form.add_error(None, "É obrigatório informar ao menos um Histórico de Vínculo Formal para Docente ou Gestão.")
            return render(request, self.template_name, {
                'form': form,
                'formacao_formset': formacao_fs,
                'experiencia_formset': experiencia_fs,
                'historico_formset': historico_fs,
                'pendencia_formset': pendencia_fs,
                'funcao_categorias': self._funcao_categorias(),
            })

        # Universal — qualquer categoria
        pendencias = _linhas_preenchidas(pendencia_fs.cleaned_data, _CAMPO_PREENCHIDO['pendencia'])

        try:
            pessoa, atribuicao, dados_docente = CadastrarPessoaComFuncaoService().executar(
                dados_pessoa=dados_pessoa,
                funcao=funcao,
                dados_atribuicao=dados_atribuicao,
                dados_extensao=dados_extensao,
                formacoes=formacoes,
                experiencias=experiencias,
                historico_vinculo_formal=historico_vinculo_formal,
                pendencias=pendencias,
            )
        except ValidationError as e:
            form.add_error(None, str(e))
            return render(request, self.template_name, {
                'form': form,
                'formacao_formset': formacao_fs,
                'experiencia_formset': experiencia_fs,
                'historico_formset': historico_fs,
                'pendencia_formset': pendencia_fs,
                'funcao_categorias': self._funcao_categorias(),
            })

        if dados_docente is not None:
            return redirect('preencher-requisitos-docente', pk=dados_docente.id)

        return redirect('detalhe-pessoa', pk=pessoa.id)


class PreencherRequisitosDocenteView(View):
    """
    Template View — PLACEHOLDER (a completar quando os Requisitos de Contratação
    e Disciplinas/Capacidade forem implementados na tela).

    Recebe o id de um DadosDocente já existente via URL (não busca por CPF/nome
    de novo — o botão "Preencher Requisitos de Contratação" já sabe qual Docente
    acabou de ser cadastrado). Hoje já mostra e permite gerenciar as Formações
    (CRUD independente, ver docs/21), além de confirmar que o Docente existe.

    NOTA (02/09/2026): decisão tomada de eliminar esta tela e consolidar tudo
    em detalhe.html, movendo o CRUD de Formação para lá — mas essa mudança
    (Etapa B) ainda NÃO foi executada. Esta View e seus botões continuam
    funcionando normalmente até essa etapa ser feita numa sessão futura.
    """
    template_name = 'cadastros/preencher_requisitos_docente.html'

    def get(self, request, pk):
        dados_docente = get_object_or_404(DadosDocente, pk=pk)
        return render(request, self.template_name, {'dados_docente': dados_docente})


class ModalCrudMixin:
    """
    Permite que a mesma View sirva tanto uma página completa (fallback sem
    JavaScript, acessando a URL direto) quanto um fragmento carregado via
    fetch() dentro de um popup/modal — o parâmetro ?parcial=1 na URL sinaliza
    o pedido do modal, retornando só o <form>, sem o layout do site em volta.
    No sucesso de um POST parcial, devolve JSON em vez de redirect, para o
    JavaScript do modal saber que deu certo (ver static/cadastros/js/
    modal-crud.js). Funciona tanto para CreateView/UpdateView (via form_valid)
    quanto para DeleteView (via delete) — mesmo mecanismo nos dois casos.

    `template_fragmento` é obrigatório em cada subclasse — cada entidade tem
    seu próprio fragmento (Formação, Histórico de Vínculo, Experiência
    Profissional, Pendência de Cadastro, Requisito de Contratação). A
    confirmação de exclusão usa um fragmento genérico único
    (`_confirmar_exclusao_fragment.html`), reaproveitado por todas as
    entidades que permitem Delete real.
    """
    template_fragmento = None

    def eh_parcial(self):
        return self.request.GET.get('parcial') == '1'

    def get_template_names(self):
        if self.eh_parcial():
            assert self.template_fragmento, (
                f"{self.__class__.__name__} precisa definir template_fragmento"
            )
            return [self.template_fragmento]
        return [self.template_name]

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.eh_parcial():
            return JsonResponse({'sucesso': True})
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if self.eh_parcial():
            return JsonResponse({'sucesso': True})
        return response


class AdicionarFormacaoDocenteView(ModalCrudMixin, CreateView):
    """
    CRUD independente (piloto da migração de arquitetura descrita em docs/21):
    adiciona uma FormacaoDocente a um Docente já existente, persistindo direto
    no banco via ModelForm — sem Formset, sem cloneNode(), sem TOTAL_FORMS.

    Segurança: o DadosDocente "pai" é resolvido em dispatch() a partir do
    <int:pk> da URL, nunca de um campo do POST — impede que alguém anexe uma
    Formação a um Docente que não é o pretendido só editando a URL.
    """
    model = FormacaoDocente
    form_class = FormacaoDocenteModelForm
    template_name = 'cadastros/form_formacao.html'
    template_fragmento = 'cadastros/_form_formacao_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.dados_docente = get_object_or_404(DadosDocente, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.dados_docente = self.dados_docente
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dados_docente'] = self.dados_docente
        context['editando'] = False
        return context

    def get_success_url(self):
        return reverse('preencher-requisitos-docente', kwargs={'pk': self.dados_docente.pk})


class EditarFormacaoDocenteView(ModalCrudMixin, UpdateView):
    """
    Segunda metade do CRUD independente de FormacaoDocente: edita um registro
    já existente. Não recebe o pk do Docente pela URL — o objeto já sabe a
    quem pertence via `self.object.dados_docente`.
    """
    model = FormacaoDocente
    form_class = FormacaoDocenteModelForm
    template_name = 'cadastros/form_formacao.html'
    template_fragmento = 'cadastros/_form_formacao_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dados_docente'] = self.object.dados_docente
        context['editando'] = True
        return context

    def get_success_url(self):
        return reverse('preencher-requisitos-docente', kwargs={'pk': self.object.dados_docente_id})


class ExcluirFormacaoDocenteView(ModalCrudMixin, DeleteView):
    """
    Terceira e última metade do CRUD de FormacaoDocente: exclusão real
    (diferente de HistoricoVinculoFormal, que nunca permite Delete). Usa o
    fragmento genérico de confirmação, compartilhado com qualquer outra
    entidade que permita Delete real.
    """
    model = FormacaoDocente
    template_name = 'cadastros/confirmar_exclusao.html'
    template_fragmento = 'cadastros/_confirmar_exclusao_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_voltar'] = reverse('preencher-requisitos-docente', kwargs={'pk': self.object.dados_docente_id})
        return context

    def get_success_url(self):
        return reverse('preencher-requisitos-docente', kwargs={'pk': self.object.dados_docente_id})


class AdicionarHistoricoVinculoFormalView(ModalCrudMixin, CreateView):
    """
    Adiciona um NOVO período de Vínculo Formal a uma AtribuicaoFuncao já
    existente (Docente ou Gestão) — ex: quando a entidade contratante muda
    ao longo do tempo (FAPETI até 2026, FUSSUSS a partir de 2026). A
    AtribuicaoFuncao "pai" é resolvida pela URL, nunca por um campo do POST.
    Acessível pela tela de detalhe da Pessoa (docs/21).
    """
    model = HistoricoVinculoFormal
    form_class = HistoricoVinculoFormalModelForm
    template_name = 'cadastros/form_historico_vinculo.html'
    template_fragmento = 'cadastros/_form_historico_vinculo_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.atribuicao = get_object_or_404(AtribuicaoFuncao, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.atribuicao = self.atribuicao
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.atribuicao
        context['encerrando'] = False
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.atribuicao.pessoa_id})


class EncerrarHistoricoVinculoFormalView(ModalCrudMixin, UpdateView):
    """
    Encerra um período de Vínculo Formal já existente — nunca Delete, só
    preenche 'data_fim' (mais 'observacao' opcional, para registrar erro de
    cadastro ou contexto). Usa EncerrarHistoricoVinculoFormalForm (só esses
    2 campos), não o ModelForm completo — impede reabrir vinculo_formal/
    data_inicio por engano.
    """
    model = HistoricoVinculoFormal
    form_class = EncerrarHistoricoVinculoFormalForm
    template_name = 'cadastros/form_historico_vinculo.html'
    template_fragmento = 'cadastros/_form_historico_vinculo_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.object.atribuicao
        context['encerrando'] = True
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})


class AdicionarExperienciaProfissionalView(ModalCrudMixin, CreateView):
    """
    CRUD independente de ExperienciaProfissional (Gestão) — mesma estrutura
    de AdicionarFormacaoDocenteView, mas o pai é uma AtribuicaoFuncao, não
    um DadosDocente. Diferente de HistoricoVinculoFormal, esta entidade
    permite Delete real.
    """
    model = ExperienciaProfissional
    form_class = ExperienciaProfissionalModelForm
    template_name = 'cadastros/form_experiencia.html'
    template_fragmento = 'cadastros/_form_experiencia_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.atribuicao = get_object_or_404(AtribuicaoFuncao, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.atribuicao = self.atribuicao
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.atribuicao
        context['editando'] = False
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.atribuicao.pessoa_id})


class EditarExperienciaProfissionalView(ModalCrudMixin, UpdateView):
    """Edita uma ExperienciaProfissional já existente."""
    model = ExperienciaProfissional
    form_class = ExperienciaProfissionalModelForm
    template_name = 'cadastros/form_experiencia.html'
    template_fragmento = 'cadastros/_form_experiencia_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.object.atribuicao
        context['editando'] = True
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})


class ExcluirExperienciaProfissionalView(ModalCrudMixin, DeleteView):
    """
    Exclusão real de ExperienciaProfissional — usa o mesmo fragmento
    genérico de confirmação que ExcluirFormacaoDocenteView.
    """
    model = ExperienciaProfissional
    template_name = 'cadastros/confirmar_exclusao.html'
    template_fragmento = 'cadastros/_confirmar_exclusao_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_voltar'] = reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})


class AdicionarPendenciaCadastroView(ModalCrudMixin, CreateView):
    """
    CRUD independente de PendenciaCadastro — universal, qualquer categoria
    (Discente/Docente/Gestão), diferente de Experiência/Histórico que são
    condicionais. O pai é uma AtribuicaoFuncao, resolvida pela URL.
    """
    model = PendenciaCadastro
    form_class = PendenciaCadastroModelForm
    template_name = 'cadastros/form_pendencia.html'
    template_fragmento = 'cadastros/_form_pendencia_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.atribuicao = get_object_or_404(AtribuicaoFuncao, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.atribuicao = self.atribuicao
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.atribuicao
        context['editando'] = False
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.atribuicao.pessoa_id})


class EditarPendenciaCadastroView(ModalCrudMixin, UpdateView):
    """
    Edita uma PendenciaCadastro já existente, incluindo marcar como
    resolvida. 'resolvida_em' é preenchido/limpo automaticamente aqui
    (não é campo do EditarPendenciaCadastroForm) — evita o usuário digitar
    uma data manual incoerente com o clique real de "resolvida".
    """
    model = PendenciaCadastro
    form_class = EditarPendenciaCadastroForm
    template_name = 'cadastros/form_pendencia.html'
    template_fragmento = 'cadastros/_form_pendencia_fragment.html'

    def form_valid(self, form):
        if form.instance.resolvida and not form.instance.resolvida_em:
            form.instance.resolvida_em = timezone.now()
        elif not form.instance.resolvida:
            form.instance.resolvida_em = None
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atribuicao'] = self.object.atribuicao
        context['editando'] = True
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})


class ExcluirPendenciaCadastroView(ModalCrudMixin, DeleteView):
    """Exclusão real de PendenciaCadastro — mesmo fragmento genérico de confirmação."""
    model = PendenciaCadastro
    template_name = 'cadastros/confirmar_exclusao.html'
    template_fragmento = 'cadastros/_confirmar_exclusao_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_voltar'] = reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.atribuicao.pessoa_id})


class EditarRequisitoContratacaoView(ModalCrudMixin, UpdateView):
    """
    Edita os Requisitos de Contratação (RBAC 141) de uma AtribuicaoFuncao já
    existente — Docente ou Gestão. Diferente das outras entidades do CRUD
    independente, não é uma lista repetível: não há Adicionar nem Excluir,
    só Editar 2 campos direto na própria AtribuicaoFuncao (não precisa de
    dispatch() resolvendo um "pai" — o objeto editado já é o pai).
    """
    model = AtribuicaoFuncao
    form_class = EditarRequisitoContratacaoForm
    template_name = 'cadastros/form_requisito_contratacao.html'
    template_fragmento = 'cadastros/_form_requisito_contratacao_fragment.html'

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.pessoa_id})
