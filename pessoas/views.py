"""
pessoas/views.py

Views (API): traduzem HTTP <-> Service. Não contêm regra de negócio.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import BuscarEnderecoPorCepService
from .serializers import BuscarCepInputSerializer, EnderecoOutputSerializer

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import FuncaoGestao, Habilitacao
from .services import BuscarEnderecoPorCepService, AssociarHabilitacaoService
from .serializers import (
    BuscarCepInputSerializer, EnderecoOutputSerializer,
    FuncaoGestaoHabilitacaoInputSerializer, FuncaoGestaoHabilitacaoOutputSerializer,
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
    

class AssociarHabilitacaoView(APIView):
    """
    SRP: única responsabilidade é traduzir HTTP <-> AssociarHabilitacaoService.
    """

    def post(self, request):
        input_serializer = FuncaoGestaoHabilitacaoInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        funcao_gestao = get_object_or_404(
            FuncaoGestao, pk=input_serializer.validated_data['funcao_gestao_id']
        )
        habilitacao = get_object_or_404(
            Habilitacao, pk=input_serializer.validated_data['habilitacao_id']
        )

        try:
            resultado = AssociarHabilitacaoService().executar(funcao_gestao, habilitacao)
        except ValidationError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = FuncaoGestaoHabilitacaoOutputSerializer({
            "id": resultado.id,
            "funcao_gestao_id": resultado.funcao_gestao_id,
            "habilitacao_id": resultado.habilitacao_id,
        })
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)