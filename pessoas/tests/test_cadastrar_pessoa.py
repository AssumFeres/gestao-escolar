import pytest
from django.core.exceptions import ValidationError
from pessoas.models import Pessoa, VinculoDiscente, VinculoDocente
from pessoas.services import CadastrarPessoaComVinculoService


def _dados_pessoa(cpf):
    return {
        "nome_completo": "Maria Teste",
        "cpf": cpf,
        "data_nascimento": "1995-03-20",
        "email": f"{cpf}@x.com",
        "telefone": "11988887777",
        "endereco_cep": "04567000",
        "endereco_logradouro": "Rua Nova",
        "endereco_numero": "200",
        "endereco_complemento": "",
        "endereco_bairro": "Vila X",
        "endereco_cidade": "São Paulo",
        "endereco_uf": "SP",
    }


@pytest.mark.django_db
class TestCadastrarPessoaComVinculoService:

    def test_cadastra_pessoa_com_vinculo_discente(self):
        pessoa, vinculo = CadastrarPessoaComVinculoService().executar(
            dados_pessoa=_dados_pessoa("22233344455"),
            tipo_vinculo="DISCENTE",
            dados_vinculo={
                "data_inicio": "2024-02-01",
                "numero_matricula": "2024001",
                "situacao": "ATIVO",
            },
        )

        assert Pessoa.objects.filter(cpf="22233344455").exists()
        assert isinstance(vinculo, VinculoDiscente)
        assert vinculo.pessoa == pessoa
        assert vinculo.numero_matricula == "2024001"

    def test_cadastra_pessoa_com_vinculo_docente(self):
        pessoa, vinculo = CadastrarPessoaComVinculoService().executar(
            dados_pessoa=_dados_pessoa("33344455566"),
            tipo_vinculo="DOCENTE",
            dados_vinculo={
                "data_inicio": "2024-02-01",
                "situacao": "ATIVO",
            },
        )

        assert isinstance(vinculo, VinculoDocente)
        assert vinculo.pessoa == pessoa

    def test_rejeita_tipo_de_vinculo_invalido(self):
        with pytest.raises(ValidationError, match="Tipo de vínculo inválido"):
            CadastrarPessoaComVinculoService().executar(
                dados_pessoa=_dados_pessoa("44455566677"),
                tipo_vinculo="ESTAGIARIO",
                dados_vinculo={"data_inicio": "2024-02-01"},
            )

    def test_nao_cria_pessoa_quando_tipo_vinculo_invalido(self):
        """Confirma que a transação atômica reverte tudo em caso de erro."""
        try:
            CadastrarPessoaComVinculoService().executar(
                dados_pessoa=_dados_pessoa("55566677788"),
                tipo_vinculo="ESTAGIARIO",
                dados_vinculo={"data_inicio": "2024-02-01"},
            )
        except ValidationError:
            pass

        assert not Pessoa.objects.filter(cpf="55566677788").exists()

