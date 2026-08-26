"""
pessoas/services.py

Camada de Services: regras de negócio que envolvem mais de uma entidade,
ou que precisam de validação além do que o Model sozinho garante.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from infraestrutura.cep.adapters import ViaCepClient


class CadastrarPessoaComVinculoService:
    """
    SRP: orquestra a criação de Pessoa + seu primeiro Vinculo numa transação única.
    Não conhece Django View nem API externa — só recebe dados já validados.
    """

    def executar(self, dados_pessoa: dict, tipo_vinculo: str, dados_vinculo: dict):
        from .models import Pessoa, VinculoDiscente, VinculoDocente, VinculoGestao

        mapa_vinculo = {
            'DISCENTE': VinculoDiscente,
            'DOCENTE': VinculoDocente,
            'GESTAO': VinculoGestao,
        }
        ModelVinculo = mapa_vinculo.get(tipo_vinculo)
        if ModelVinculo is None:
            raise ValidationError(f"Tipo de vínculo inválido: {tipo_vinculo}")

        with transaction.atomic():
            pessoa = Pessoa.objects.create(**dados_pessoa)
            vinculo = ModelVinculo.objects.create(pessoa=pessoa, **dados_vinculo)

        return pessoa, vinculo


class BuscarEnderecoPorCepService:
    """DIP: depende da abstração (porta), não da implementação concreta (ViaCEP)."""

    def __init__(self, cliente_cep=None):
        self.cliente_cep = cliente_cep or ViaCepClient()

    def executar(self, cep: str):
        return self.cliente_cep.buscar_endereco(cep)