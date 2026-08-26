"""
pessoas/views.py

Views (API): traduzem HTTP <-> Service. Não contêm regra de negócio.
"""
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Pessoa
from .forms import CadastrarPessoaForm
from .services import (
    BuscarEnderecoPorCepService,
    CadastrarPessoaComVinculoService,
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
    SRP: única responsabilidade é traduzir HTTP <-> CadastrarPessoaComVinculoService.
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

        dados_vinculo = {
            "data_inicio": dados["data_inicio"],
            "situacao": dados["situacao"],
        }
        if dados["tipo_vinculo"] == "DISCENTE":
            dados_vinculo["numero_matricula"] = dados.get("numero_matricula", "")

        try:
            pessoa, vinculo = CadastrarPessoaComVinculoService().executar(
                dados_pessoa=dados_pessoa,
                tipo_vinculo=dados["tipo_vinculo"],
                dados_vinculo=dados_vinculo,
            )
        except ValidationError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = CadastrarPessoaOutputSerializer({
            "pessoa_id": pessoa.id,
            "nome_completo": pessoa.nome_completo,
            "tipo_vinculo": dados["tipo_vinculo"],
            "vinculo_id": vinculo.id,
        })
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ListaPessoasView(ListView):
    """
    Template View: renderiza HTML no servidor, sem passar por Serializer/JSON.
    """
    model = Pessoa
    template_name = 'pessoas/lista.html'
    context_object_name = 'pessoas'


class DetalhePessoaView(DetailView):
    """
    Template View: mostra os dados completos de uma Pessoa e seus vinculos.
    """
    model = Pessoa
    template_name = 'pessoas/detalhe.html'
    context_object_name = 'pessoa'


class NovoCadastroPessoaView(View):
    """
    Template View: formulario HTML de cadastro. Reusa o mesmo Service
    da API (CadastrarPessoaComVinculoService) — mesma regra de negocio,
    caminho de entrada diferente.
    """
    template_name = 'pessoas/form_pessoa.html'

    def get(self, request):
        form = CadastrarPessoaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CadastrarPessoaForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        dados = form.cleaned_data

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

        dados_vinculo = {
            "data_inicio": dados["data_inicio"],
            "situacao": dados["situacao"],
        }
        if dados["tipo_vinculo"] == "DISCENTE":
            dados_vinculo["numero_matricula"] = dados.get("numero_matricula", "")

        try:
            pessoa, vinculo = CadastrarPessoaComVinculoService().executar(
                dados_pessoa=dados_pessoa,
                tipo_vinculo=dados["tipo_vinculo"],
                dados_vinculo=dados_vinculo,
            )
        except ValidationError as e:
            form.add_error(None, str(e))
            return render(request, self.template_name, {'form': form})

        return redirect('detalhe-pessoa', pk=pessoa.id)