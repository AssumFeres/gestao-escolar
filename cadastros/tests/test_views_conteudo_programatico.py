import pytest
from django.urls import reverse

from cadastros.models import ConteudoProgramatico, Disciplina


@pytest.fixture
def disciplina_com_kp(db):
    disciplina = Disciplina.objects.create(
        nome='Disciplina de teste de KP', sigla='KPT',
        carga_horaria_programa_de_instrucao=40,
        carga_horaria_teorica=20, carga_horaria_pratica=20,
    )
    ConteudoProgramatico.objects.create(
        disciplina=disciplina, ordem=1, descricao='Conteúdo original',
    )
    return disciplina


def url_formulario(nome, pk, parcial):
    url = reverse(nome, kwargs={'pk': pk})
    return url + '?parcial=1' if parcial else url


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_criar_kp_repetido_retorna_erro_no_campo(client, disciplina_com_kp, parcial):
    disciplina = disciplina_com_kp
    url = url_formulario('adicionar-conteudo-programatico', disciplina.pk, parcial)
    response = client.post(url, {'ordem': 1, 'descricao': 'Conteúdo repetido'})

    assert response.status_code == 200
    assert 'ordem' in response.context['form'].errors
    assert response.context['form'].errors['ordem'] == [
        'Não foi possível salvar porque este número de ordem já está em uso. '
        'Informe um número ainda não utilizado. '
        'Os dados preenchidos foram mantidos no formulário. '
        'Corrija o número de ordem e tente novamente ou feche a janela para cancelar.'
    ]
    html = response.content.decode()
    destino = reverse('detalhe-disciplina', kwargs={'pk': disciplina.pk})
    assert '<button type="submit" form="form-cancelar-conteudo-programatico" class="btn-cancelar" data-fechar-modal-crud>Cancelar</button>' in html
    assert f'<form id="form-cancelar-conteudo-programatico" method="get" action="{destino}"></form>' in html
    assert '<button type="submit" class="btn-salvar">Salvar Item</button>' in html
    assert 'aria-invalid="true"' in html
    assert 'href="#id_ordem"' in html
    assert '<a href="#id_ordem">Ordem</a>' in html
    assert html.count('Não foi possível salvar porque este número de ordem já está em uso.') == 1
    assert 'id="id_ordem_error"' in html
    assert 'Conteúdo repetido' in html
    assert disciplina.conteudos_programaticos.count() == 1

    corrigida = client.post(url, {'ordem': 2, 'descricao': 'Conteúdo corrigido'})
    assert corrigida.status_code == (200 if parcial else 302)
    if parcial:
        assert corrigida.json() == {'sucesso': True}
    assert disciplina.conteudos_programaticos.filter(
        ordem=2, descricao='Conteúdo corrigido',
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_editar_para_kp_repetido_preserva_conteudo(client, disciplina_com_kp, parcial):
    item = ConteudoProgramatico.objects.create(
        disciplina=disciplina_com_kp, ordem=2, descricao='Segundo conteúdo',
    )
    url = url_formulario('editar-conteudo-programatico', item.pk, parcial)
    response = client.post(url, {'ordem': 1, 'descricao': 'Tentativa de alteração'})

    assert response.status_code == 200
    assert 'ordem' in response.context['form'].errors
    item.refresh_from_db()
    assert item.ordem == 2
    assert item.descricao == 'Segundo conteúdo'


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_editar_mantendo_kp_atual_e_permitido(client, disciplina_com_kp, parcial):
    item = disciplina_com_kp.conteudos_programaticos.get(ordem=1)
    url = url_formulario('editar-conteudo-programatico', item.pk, parcial)
    response = client.post(url, {'ordem': 1, 'descricao': 'Conteúdo atualizado'})

    assert response.status_code == (200 if parcial else 302)
    if parcial:
        assert response.json() == {'sucesso': True}
    item.refresh_from_db()
    assert item.ordem == 1
    assert item.descricao == 'Conteúdo atualizado'


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
def test_mesmo_kp_em_outra_disciplina_e_permitido(client, disciplina_com_kp, parcial):
    outra = Disciplina.objects.create(
        nome='Outra disciplina de KP', sigla='KPO',
        carga_horaria_programa_de_instrucao=40,
        carga_horaria_teorica=20, carga_horaria_pratica=20,
    )
    url = url_formulario('adicionar-conteudo-programatico', outra.pk, parcial)
    response = client.post(url, {'ordem': 1, 'descricao': 'Conteúdo em outra disciplina'})

    assert response.status_code == (200 if parcial else 302)
    if parcial:
        assert response.json() == {'sucesso': True}
    assert outra.conteudos_programaticos.filter(ordem=1).exists()
    assert disciplina_com_kp.conteudos_programaticos.count() == 1
