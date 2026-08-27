import pytest
from django.core.exceptions import ValidationError
from pessoas.models import Pessoa, Funcao, AtribuicaoFuncao, DadosDiscente
from pessoas.services import CadastrarPessoaComFuncaoService


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
class TestCadastrarPessoaComFuncaoService:

    def test_cadastra_pessoa_nova_com_funcao(self):
        funcao = Funcao.objects.create(nome="Docente - Instrutor", categoria="DOCENTE")

        pessoa, atribuicao, dados_docente = CadastrarPessoaComFuncaoService().executar(
            dados_pessoa=_dados_pessoa("22233344455"),
            funcao=funcao,
            dados_atribuicao={"data_inicio": "2024-02-01", "situacao": "ATIVO"},
        )

        assert Pessoa.objects.filter(cpf="22233344455").exists()
        assert atribuicao.pessoa == pessoa
        assert atribuicao.funcao == funcao
        assert dados_docente is not None
        assert dados_docente.atribuicao == atribuicao

    def test_reaproveita_pessoa_existente_pelo_cpf(self):
        """Coração da Etapa 6: segunda Função para o mesmo CPF não duplica Pessoa."""
        funcao_1 = Funcao.objects.create(nome="Docente - Instrutor", categoria="DOCENTE")
        funcao_2 = Funcao.objects.create(nome="Coordenador de Curso Aviônicos", categoria="GESTAO")

        pessoa_1, _, _ = CadastrarPessoaComFuncaoService().executar(
            dados_pessoa=_dados_pessoa("33344455566"),
            funcao=funcao_1,
            dados_atribuicao={"data_inicio": "2024-02-01", "situacao": "ATIVO"},
        )
        pessoa_2, atribuicao_2, _ = CadastrarPessoaComFuncaoService().executar(
            dados_pessoa=_dados_pessoa("33344455566"),
            funcao=funcao_2,
            dados_atribuicao={"data_inicio": "2024-03-01", "situacao": "ATIVO"},
        )

        assert pessoa_1.id == pessoa_2.id
        assert Pessoa.objects.filter(cpf="33344455566").count() == 1
        assert pessoa_2.atribuicoes.count() == 2

    def test_rejeita_acumulo_de_funcao_para_discente(self):
        """Regra verificada pela estrutura (DadosDiscente), nunca pelo nome da Funcao."""
        funcao_discente = Funcao.objects.create(nome="Discente - Aluno", categoria="DISCENTE")
        funcao_docente = Funcao.objects.create(nome="Docente - Instrutor", categoria="DOCENTE")

        pessoa = Pessoa.objects.create(**_dados_pessoa("44455566677"))
        atribuicao_discente = AtribuicaoFuncao.objects.create(
            pessoa=pessoa, funcao=funcao_discente,
            data_inicio="2024-02-01", situacao="ATIVO",
        )
        DadosDiscente.objects.create(atribuicao=atribuicao_discente)

        with pytest.raises(ValidationError, match="não pode acumular"):
            CadastrarPessoaComFuncaoService().executar(
                dados_pessoa=_dados_pessoa("44455566677"),
                funcao=funcao_docente,
                dados_atribuicao={"data_inicio": "2024-03-01", "situacao": "ATIVO"},
            )

    def test_nao_cria_segunda_atribuicao_quando_discente_tenta_acumular(self):
        """Confirma que a transação reverte por completo em caso de erro."""
        funcao_discente = Funcao.objects.create(nome="Discente - Aluno", categoria="DISCENTE")
        funcao_docente = Funcao.objects.create(nome="Docente - Instrutor", categoria="DOCENTE")

        pessoa = Pessoa.objects.create(**_dados_pessoa("55566677788"))
        atribuicao_discente = AtribuicaoFuncao.objects.create(
            pessoa=pessoa, funcao=funcao_discente,
            data_inicio="2024-02-01", situacao="ATIVO",
        )
        DadosDiscente.objects.create(atribuicao=atribuicao_discente)

        try:
            CadastrarPessoaComFuncaoService().executar(
                dados_pessoa=_dados_pessoa("55566677788"),
                funcao=funcao_docente,
                dados_atribuicao={"data_inicio": "2024-03-01", "situacao": "ATIVO"},
            )
        except ValidationError:
            pass

        assert pessoa.atribuicoes.count() == 1