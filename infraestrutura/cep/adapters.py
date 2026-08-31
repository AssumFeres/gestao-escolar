"""
infraestrutura/cep/adapters.py

Adaptador concreto: implementa AbstractCepClient usando a API pÃºblica ViaCEP.
"""

import requests

from cadastros.models import Endereco
from .ports import AbstractCepClient


class ViaCepClient(AbstractCepClient):
    BASE_URL = "https://viacep.com.br/ws"

    def buscar_endereco(self, cep: str) -> Endereco:
        cep_limpo = cep.replace("-", "").replace(".", "").strip()

        response = requests.get(f"{self.BASE_URL}/{cep_limpo}/json/", timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("erro"):
            raise ValueError(f"CEP nÃ£o encontrado: {cep}")

        return Endereco(
            cep=cep_limpo,
            logradouro=data.get("logradouro", ""),
            numero="",  # ViaCEP nÃ£o retorna nÃºmero â€” usuÃ¡rio preenche depois
            complemento=data.get("complemento", ""),
            bairro=data.get("bairro", ""),
            cidade=data.get("localidade", ""),
            uf=data.get("uf", ""),
        )


