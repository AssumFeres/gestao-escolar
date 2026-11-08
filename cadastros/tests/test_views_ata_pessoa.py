from datetime import date

import pytest
from django.urls import reverse

from cadastros.forms import AtaPessoaModelForm
from cadastros.models import (
    Ata, AtaPessoa, Pessoa, Funcao, AtribuicaoFuncao, DadosDiscente,
    SituacaoAtribuicao,
)


@pytest.fixture
def cenario_ata_pessoa(db):
    ata = Ata.objects.create(
        numero='001/2026', tipo=Ata._meta.get_field('tipo').choices[0][0],
        finalidade='OUTRO', data=date(2026, 1, 1),
    )
    discente = Funcao.objects.create(nome='Discente teste Ata', categoria='DISCENTE')
    docente = Funcao.objects.create(nome='Docente teste Ata', categoria='DOCENTE')

    def pessoa(indice):
        return Pessoa.objects.create(
            nome_completo=f'Pessoa {indice}', cpf=f'{indice:011d}',
            data_nascimento=date(1990, 1, 1), email=f'pessoa{indice}@teste.com',
            telefone='11999999999',
        )

    def atribuir(pessoa, funcao, situacao):
        atribuicao = AtribuicaoFuncao.objects.create(
            pessoa=pessoa, funcao=funcao, situacao=situacao,
            data_inicio=date(2026, 1, 1),
        )
        if funcao == discente:
            DadosDiscente.objects.create(atribuicao=atribuicao)

    ativa, inativa, professora, mista, sem_atribuicao = [pessoa(i) for i in range(1, 6)]
    atribuir(ativa, discente, SituacaoAtribuicao.ATIVO)
    atribuir(inativa, discente, SituacaoAtribuicao.INATIVO)
    atribuir(professora, docente, SituacaoAtribuicao.ATIVO)
    # A atribuição ativa de outra categoria não pode tornar o vínculo antigo elegível.
    atribuir(mista, discente, SituacaoAtribuicao.INATIVO)
    atribuir(mista, docente, SituacaoAtribuicao.ATIVO)
    return dict(ata=ata, ativa=ativa, inativa=inativa, docente=professora,
                mista=mista, sem_atribuicao=sem_atribuicao)


def url_vinculo(ata, parcial):
    url = reverse('adicionar-ata-pessoa', kwargs={'pk': ata.pk})
    return url + '?parcial=1' if parcial else url


@pytest.mark.django_db
def test_opcoes_exigem_discente_ativo_na_mesma_atribuicao(cenario_ata_pessoa):
    c = cenario_ata_pessoa
    form = AtaPessoaModelForm(ata=c['ata'])
    assert list(form.fields['pessoa'].queryset) == [c['ativa']]


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_abrir_vinculo_pessoa_ata_sem_field_error(client, cenario_ata_pessoa, parcial):
    c = cenario_ata_pessoa
    response = client.get(url_vinculo(c['ata'], parcial))
    assert response.status_code == 200
    assert list(response.context['form'].fields['pessoa'].queryset) == [c['ativa']]
    assert 'id="id_pessoa"' in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_vincular_discente_ativo_a_ata(client, cenario_ata_pessoa, parcial):
    c = cenario_ata_pessoa
    response = client.post(url_vinculo(c['ata'], parcial), {'pessoa': c['ativa'].pk})
    assert response.status_code == (200 if parcial else 302)
    if parcial:
        assert response.json() == {'sucesso': True}
    else:
        assert response.url == reverse('detalhe-ata', kwargs={'pk': c['ata'].pk})
    assert AtaPessoa.objects.filter(ata=c['ata'], pessoa=c['ativa']).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
@pytest.mark.parametrize('inelegivel', ['inativa', 'docente', 'mista', 'sem_atribuicao'])
def test_post_nao_vincula_pessoa_inelegivel(client, cenario_ata_pessoa, parcial, inelegivel):
    c = cenario_ata_pessoa
    response = client.post(url_vinculo(c['ata'], parcial), {'pessoa': c[inelegivel].pk})
    assert response.status_code == 200
    assert 'pessoa' in response.context['form'].errors
    assert 'aria-invalid="true"' in response.content.decode()
    assert not AtaPessoa.objects.filter(ata=c['ata']).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_vinculo_duplicado_retorna_erro_e_preserva_registro(client, cenario_ata_pessoa, parcial):
    c = cenario_ata_pessoa
    AtaPessoa.objects.create(ata=c['ata'], pessoa=c['ativa'])
    response = client.post(url_vinculo(c['ata'], parcial), {'pessoa': c['ativa'].pk})
    assert response.status_code == 200
    assert 'pessoa' in response.context['form'].errors
    assert '<a href="#id_pessoa">Pessoa</a>' in response.content.decode()
    assert AtaPessoa.objects.filter(ata=c['ata'], pessoa=c['ativa']).count() == 1
