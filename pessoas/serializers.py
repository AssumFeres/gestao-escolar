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


class CadastrarPessoaInputSerializer(serializers.Serializer):
    """
    Serializer de ENTRADA — dados da Pessoa + tipo de vínculo + dados específicos do vínculo.
    Campos de vínculo são opcionais na entrada porque variam por tipo; a validação
    de qual é obrigatório para cada tipo continua no Service, não aqui.
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

    # Tipo e dados do Vínculo
    tipo_vinculo = serializers.ChoiceField(choices=["DISCENTE", "DOCENTE", "GESTAO"])
    data_inicio = serializers.DateField()
    situacao = serializers.CharField(max_length=30, default="ATIVO")
    numero_matricula = serializers.CharField(max_length=20, required=False, allow_blank=True)


class CadastrarPessoaOutputSerializer(serializers.Serializer):
    pessoa_id = serializers.IntegerField()
    nome_completo = serializers.CharField()
    tipo_vinculo = serializers.CharField()
    vinculo_id = serializers.IntegerField()

