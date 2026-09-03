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
    CadastrarPessoaForm, EditarPessoaForm, FormacaoDocenteModelForm,
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
    BuscarPessoaPorCpfInputSerializer, PessoaOutputSerializer,
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


class BuscarPessoaPorCpfView(APIView):
    """
    SRP: busca uma Pessoa por CPF, para pré-preencher o formulário de
    cadastro quando o CPF já existir — parte da funcionalidade de
    reaproveitamento/edição de dados (docs/27). Só leitura, nunca cria
    nem altera nada — a atualização de verdade só acontece se o formulário
    for submetido depois (via CadastrarPessoaComFuncaoService).
    """

    def get(self, request, cpf):
        input_serializer = BuscarPessoaPorCpfInputSerializer(data={"cpf": cpf})
        input_serializer.is_valid(raise_exception=True)

        pessoa = Pessoa.objects.filter(cpf=input_serializer.validated_data["cpf"]).first()
        if not pessoa:
            return Response({"encontrada": False}, status=status.HTTP_200_OK)

        output_serializer = PessoaOutputSerializer(pessoa)
        return Response({"encontrada": True, "pessoa": output_serializer.data}, status=status.HTTP_200_OK)


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
    Único "centro de comando" da Pessoa desde a Etapa B (02/09/2026).
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

    Busca por CPF (docs/27): o campo CPF, ao apertar Enter, consulta
    /api/cadastros/pessoa-por-cpf/<cpf>/ e pré-preenche os demais campos
    se a Pessoa já existir — ver static/cadastros/js/buscar-cpf.js. Isso é
    só front-end; o back-end sempre aceita o POST completo normalmente,
    e o Service decide se cria ou atualiza a Pessoa pelo CPF.
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

        # Requisitos de Contratação (RBAC 141) — todos exceto Discente.
        if funcao.categoria != CategoriaFuncao.DISCENTE:
            dados_atribuicao["requisito_contratacao"] = dados.get("requisito_contratacao", "")
            dados_atribuicao["documento_comprobatorio"] = dados.get("documento_comprobatorio", "")

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

        return redirect('detalhe-pessoa', pk=pessoa.id)


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


class EditarPessoaView(ModalCrudMixin, UpdateView):
    """Edita os campos comuns da Pessoa (identificação + endereço)."""
    model = Pessoa
    form_class = EditarPessoaForm
    template_name = 'cadastros/form_pessoa_editar.html'
    template_fragmento = 'cadastros/_form_pessoa_editar_fragment.html'

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.pk})


class AdicionarFormacaoDocenteView(ModalCrudMixin, CreateView):
    """Adiciona uma FormacaoDocente a um Docente já existente."""
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
        return reverse('detalhe-pessoa', kwargs={'pk': self.dados_docente.atribuicao.pessoa_id})


class EditarFormacaoDocenteView(ModalCrudMixin, UpdateView):
    """Edita um registro de Formação já existente."""
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
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.dados_docente.atribuicao.pessoa_id})


class ExcluirFormacaoDocenteView(ModalCrudMixin, DeleteView):
    """Exclusão real de FormacaoDocente."""
    model = FormacaoDocente
    template_name = 'cadastros/confirmar_exclusao.html'
    template_fragmento = 'cadastros/_confirmar_exclusao_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_voltar'] = reverse('detalhe-pessoa', kwargs={'pk': self.object.dados_docente.atribuicao.pessoa_id})
        return context

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.dados_docente.atribuicao.pessoa_id})


class AdicionarHistoricoVinculoFormalView(ModalCrudMixin, CreateView):
    """Adiciona um NOVO período de Vínculo Formal a uma AtribuicaoFuncao já existente."""
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
    """Encerra um período de Vínculo Formal já existente — nunca Delete."""
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
    """CRUD independente de ExperienciaProfissional (Gestão)."""
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
    """Exclusão real de ExperienciaProfissional."""
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
    """CRUD independente de PendenciaCadastro — universal, qualquer categoria."""
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
    """Edita uma PendenciaCadastro já existente, incluindo marcar como resolvida."""
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
    """Exclusão real de PendenciaCadastro."""
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
    """Edita os Requisitos de Contratação (RBAC 141) de uma AtribuicaoFuncao já existente."""
    model = AtribuicaoFuncao
    form_class = EditarRequisitoContratacaoForm
    template_name = 'cadastros/form_requisito_contratacao.html'
    template_fragmento = 'cadastros/_form_requisito_contratacao_fragment.html'

    def get_success_url(self):
        return reverse('detalhe-pessoa', kwargs={'pk': self.object.pessoa_id})
