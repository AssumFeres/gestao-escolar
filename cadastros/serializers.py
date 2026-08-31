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


class CadastrarPessoaInputSerializer(serializers.Serializer):
    """
    Serializer de ENTRADA — dados da Pessoa + Função a atribuir + dados da atribuição.
    Não cria extensões (DadosDiscente/DadosDocente) — isso é responsabilidade
    da Etapa 7, quando os formulários especializados por categoria existirem.
    """
    # Dados da Pessoa
    nome_completo = serializers.CharField(max_length=200)
    cpf = serializers.CharField(max_length=11)
    data_nascimento = serializers.DateField()
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20)
    endereco_cep = serializers.CharField(max_length=8)
    endereco_logradouro = serializers.CharField(max_length=200)
    endereco_numero = serializers.CharField(max_length=10)
    endereco_complemento = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
    endereco_bairro = serializers.CharField(max_length=100)
    endereco_cidade = serializers.CharField(max_length=100)
    endereco_uf = serializers.CharField(max_length=2)

    # Função a atribuir
    funcao_id = serializers.IntegerField()
    data_inicio = serializers.DateField()
    situacao = serializers.CharField(max_length=30, default="ATIVO")


class CadastrarPessoaOutputSerializer(serializers.Serializer):
    pessoa_id = serializers.IntegerField()
    nome_completo = serializers.CharField()
    funcao = serializers.CharField()
    atribuicao_id = serializers.IntegerField()

    