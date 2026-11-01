"""
infraestrutura/cep/ports.py

Porta (interface abstrata) para busca de endereço por CEP.
Qualquer provedor concreto (ViaCEP, outro serviço) deve implementar esse contrato.
"""

from abc import ABC, abstractmethod

from cadastros.models import Endereco


class AbstractCepClient(ABC):
    @abstractmethod
    def buscar_endereco(self, cep: str) -> Endereco:
        ...
