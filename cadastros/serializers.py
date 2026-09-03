"""
cadastros/serializers.py

Serializers de entrada (Input) e saida (Output) - separados por ISP,
evitando contratos inchados com campos opcionais desnecessarios.
"""
from rest_framework import serializers

from .models import Pessoa


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
    Serializer de ENTRADA -- dados da Pessoa + Funcao a atribuir + dados da atribuicao.
    Nao cria extensoes (DadosDiscente/DadosDocente) -- isso e responsabilidade
    da Etapa 7, quando os formularios especializados por categoria existirem.
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
    # Funcao a atribuir
    funcao_id = serializers.IntegerField()
    data_inicio = serializers.DateField()
    situacao = serializers.CharField(max_length=30, default="ATIVO")


class CadastrarPessoaOutputSerializer(serializers.Serializer):
    pessoa_id = serializers.IntegerField()
    nome_completo = serializers.CharField()
    funcao = serializers.CharField()
    atribuicao_id = serializers.IntegerField()


class BuscarPessoaPorCpfInputSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=11)


class PessoaOutputSerializer(serializers.ModelSerializer):
    """
    Saida da busca por CPF (docs/27) -- todos os campos comuns da Pessoa,
    para pre-preencher o formulario de cadastro quando o CPF ja existir.

    ModelSerializer aqui, ao inves de Serializer manual (padrao do resto
    deste arquivo): evita declarar ~25 campos a mao so para repassar o que
    ja esta no Model -- e puramente leitura, sem logica de validacao de
    entrada (nunca e usado para receber dados, so para devolver).
    """
    class Meta:
        model = Pessoa
        fields = [
            'id', 'nome_completo', 'cpf', 'data_nascimento', 'email', 'telefone',
            'registro_matricula', 'registro_aluno', 'codigo_anac',
            'sexo', 'identidade', 'data_emissao_identidade', 'orgao_expedidor_identidade',
            'naturalidade', 'uf_naturalidade', 'nacionalidade',
            'filiacao_1', 'filiacao_2', 'nivel_instrucao', 'estado_civil', 'raca_cor',
            'endereco_cep', 'endereco_logradouro', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cidade', 'endereco_uf',
        ]
