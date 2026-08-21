"""
pessoas/views.py

Views (API): traduzem HTTP <-> Service. Não contêm regra de negócio.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import BuscarEnderecoPorCepService
from .serializers import BuscarCepInputSerializer, EnderecoOutputSerializer


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

