"""
pessoas/serializers.py

Serializers de entrada (Input) e saída (Output) - separados por ISP,
evitando contratos inchados com campos opcionais desnecessarios.
"""

from rest_framework import serializers


class BuscarCepInputSerializer(serializers.Serializer):
    cep = serializers.CharField(max_length=9)


class EnderecoOutputSerializer(serializers.Serializer):
    cep = serializers.CharField()
    logradouro = serializers.CharField()
    numero = serializers.CharField(allow_blank=True)
    complemento = serializers.CharField(allow_blank=True)
    bairro = serializers.CharField()
    cidade = serializers.CharField()
    uf = serializers.CharField()


class FuncaoGestaoHabilitacaoInputSerializer(serializers.Serializer):
    """
    Serializer de ENTRADA — só valida formato/tipo dos dados.
    NÃO valida regra de negócio (isso é papel do Service).
    """
    funcao_gestao_id = serializers.IntegerField()
    habilitacao_id = serializers.IntegerField()


class FuncaoGestaoHabilitacaoOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    funcao_gestao_id = serializers.IntegerField()
    habilitacao_id = serializers.IntegerField()