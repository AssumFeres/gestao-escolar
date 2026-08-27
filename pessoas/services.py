"""
pessoas/services.py

Camada de Services: regras de negócio que envolvem mais de uma entidade,
ou que precisam de validação além do que o Model sozinho garante.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from infraestrutura.cep.adapters import ViaCepClient


class CadastrarPessoaComFuncaoService:
    """
    SRP: orquestra o cadastro de Pessoa + AtribuicaoFuncao numa transação única,
    buscando Pessoa existente pelo CPF antes de criar uma nova (evita duplicidade
    quando a mesma pessoa acumula uma nova Função ou repete curso).

    Não cria extensões (DadosDiscente/DadosDocente) — isso é responsabilidade
    da Etapa 7, quando os formulários especializados por categoria existirem.

    Regra de negócio: uma Pessoa com Função de Discente (identificada pela
    existência de DadosDiscente associado a alguma AtribuicaoFuncao dela, nunca
    pelo texto de Funcao.nome — nome é editável, estrutura não) não pode acumular
    outra Função.
    """

    def executar(self, dados_pessoa: dict, funcao, dados_atribuicao: dict):
        from .models import Pessoa, AtribuicaoFuncao

        with transaction.atomic():
            pessoa, criada = Pessoa.objects.get_or_create(
                cpf=dados_pessoa['cpf'],
                defaults=dados_pessoa,
            )

            if not criada:
                ja_e_discente = pessoa.atribuicoes.filter(dados_discente__isnull=False).exists()
                if ja_e_discente:
                    raise ValidationError(
                        "Esta pessoa já possui a Função Discente e não pode acumular outra Função."
                    )

            atribuicao = AtribuicaoFuncao.objects.create(
                pessoa=pessoa, funcao=funcao, **dados_atribuicao
            )

        return pessoa, atribuicao


class BuscarEnderecoPorCepService:
    """DIP: depende da abstração (porta), não da implementação concreta (ViaCEP)."""

    def __init__(self, cliente_cep=None):
        self.cliente_cep = cliente_cep or ViaCepClient()

    def executar(self, cep: str):
        return self.cliente_cep.buscar_endereco(cep)