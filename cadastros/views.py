"""
cadastros/views.py

Views (API e Template): traduzem HTTP <-> Service. Não contêm regra de negócio.
"""
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Pessoa, Funcao, CategoriaFuncao, DadosDocente
from .forms import (
    CadastrarPessoaForm,
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

        # Universal — qualquer categoria
        pendencias = _linhas_preenchidas(pendencia_fs.cleaned_data, _CAMPO_PREENCHIDO['pendencia'])

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
    acabou de ser cadastrado). Hoje só confirma que o Docente foi encontrado.
    """
    template_name = 'cadastros/preencher_requisitos_docente.html'

    def get(self, request, pk):
        dados_docente = get_object_or_404(DadosDocente, pk=pk)
        return render(request, self.template_name, {'dados_docente': dados_docente})
