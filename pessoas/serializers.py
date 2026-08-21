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
    