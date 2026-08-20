import pytest
from django.core.exceptions import ValidationError
from pessoas.models import Pessoa, VinculoGestao, FuncaoGestao, Habilitacao, TipoFuncaoGestao
from pessoas.services import AssociarHabilitacaoService


def _criar_pessoa(nome, cpf):
    return Pessoa.objects.create(
        nome_completo=nome, cpf=cpf,
        data_nascimento="1980-01-01", email=f"{cpf}@x.com", telefone="11999998888",
        endereco_cep="01310100", endereco_logradouro="Av. Paulista", endereco_numero="1000",
        endereco_complemento="", endereco_bairro="Bela Vista", endereco_cidade="São Paulo", endereco_uf="SP",
    )


@pytest.mark.django_db
class TestAssociarHabilitacaoService:

    def test_associa_habilitacao_quando_funcao_e_coordenador(self):
        pessoa = _criar_pessoa("Carlos", "11122233344")
        vinculo = VinculoGestao.objects.create(pessoa=pessoa, data_inicio="2024-01-01", situacao="ATIVO")
        funcao = FuncaoGestao.objects.create(
            vinculo_gestao=vinculo, tipo_funcao=TipoFuncaoGestao.COORDENADOR, data_inicio="2024-01-01"
        )
        habilitacao = Habilitacao.objects.create(codigo="HAB-01", nome="Gestão da Qualidade")

        resultado = AssociarHabilitacaoService().executar(funcao, habilitacao)

        assert resultado.funcao_gestao == funcao
        assert resultado.habilitacao == habilitacao

    def test_rejeita_associacao_quando_funcao_nao_e_coordenador(self):
        pessoa = _criar_pessoa("Diretor X", "55566677788")
        vinculo = VinculoGestao.objects.create(pessoa=pessoa, data_inicio="2024-01-01", situacao="ATIVO")
        funcao_diretor = FuncaoGestao.objects.create(
            vinculo_gestao=vinculo, tipo_funcao=TipoFuncaoGestao.DIRETOR, data_inicio="2024-01-01"
        )
        habilitacao = Habilitacao.objects.create(codigo="HAB-02", nome="Auditoria")

        with pytest.raises(ValidationError, match="só pode ser associada a Coordenador"):
            AssociarHabilitacaoService().executar(funcao_diretor, habilitacao)
            