from datetime import date
from html.parser import HTMLParser

import pytest
from django.urls import reverse

from atribuicao.models import MatriculaTurma
from cadastros.models import (
    Ata, AtribuicaoFuncao, DadosDiscente, Funcao, Modulo, OfertaModulo,
    Pessoa, Turma,
)


class Elementos(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def formulario(self):
        forms = [attrs for tag, attrs in self.nodes if tag == 'form']
        assert len(forms) == 1
        return forms[0]


@pytest.fixture
def cenario_planejamento(db):
    modulo = Modulo.objects.create(nome='Modulo teste', sigla='BAS', categoria='BASICO')
    oferta = OfertaModulo.objects.create(
        modulo=modulo, ano_letivo=2026, data_inicio=date(2026, 1, 1),
    )
    turma = Turma.objects.create(
        oferta_modulo=oferta, nome='Turma teste', sigla='T1', periodo='MATUTINO',
    )
    funcao = Funcao.objects.create(nome='Discente teste', categoria='DISCENTE')
    atribuicoes = []
    for indice, nome in enumerate(('Zuleica Teste', 'Ana Teste'), start=1):
        pessoa = Pessoa.objects.create(
            nome_completo=nome, cpf=f'{indice:011d}', data_nascimento=date(1990, 1, 1),
            email=f'pessoa{indice}@teste.com', telefone='11999999999',
        )
        atribuicao = AtribuicaoFuncao.objects.create(
            pessoa=pessoa, funcao=funcao, data_inicio=date(2026, 1, 1),
        )
        DadosDiscente.objects.create(atribuicao=atribuicao)
        atribuicoes.append(atribuicao)
    matricula = MatriculaTurma.objects.create(turma=turma, atribuicao_funcao=atribuicoes[0])
    ata = Ata.objects.create(
        numero='001/2026', tipo='ORDINARIA', finalidade='INICIO_VINCULO',
        data=date(2026, 1, 1),
    )
    return dict(turma=turma, matricula=matricula, nova=atribuicoes[1], ata=ata)


def caminho(cenario, fluxo, parcial):
    if fluxo == 'editar':
        url = reverse('editar-matricula-turma', kwargs={'pk': cenario['matricula'].pk})
    else:
        nome = 'adicionar-matricula-turma' if fluxo == 'adicionar' else 'finalizar-planejamento'
        url = reverse(nome, kwargs={'pk': cenario['turma'].pk})
    return url + '?parcial=1' if parcial else url


def conferir_html(response, url, parcial, fluxo):
    assert response.status_code == 200
    html = response.content.decode()
    elementos = Elementos(html)
    form = elementos.formulario()
    assert form['method'] == 'post'
    assert form['action'] == url
    assert 'form-modal-crud' in form['class'].split()
    assert any(t == 'input' and a.get('name') == 'csrfmiddlewaretoken' for t, a in elementos.nodes)
    assert any(t == 'button' and a.get('class') == 'btn-salvar' for t, a in elementos.nodes)
    assert ('id="conteudo-principal"' in html) == (not parcial)
    assert any(t == 'h2' for t, _ in elementos.nodes)
    ids = [a['id'] for _, a in elementos.nodes if a.get('id')]
    assert len(ids) == len(set(ids))
    for tag, attrs in elementos.nodes:
        if tag == 'label':
            assert attrs.get('for') in ids
        for ref in attrs.get('aria-describedby', '').split():
            assert ref in ids
    if parcial:
        cancelar = 'modal-cancelar-planejamento' if fluxo == 'planejamento' else 'modal-crud-cancelar-btn'
        assert any(t == 'button' and a.get('id') == cancelar and a.get('type') == 'button'
                   and a.get('class') == 'btn-cancelar' for t, a in elementos.nodes)
    else:
        assert any(t == 'a' and a.get('class') == 'btn-cancelar' for t, a in elementos.nodes)
    return html, elementos


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
@pytest.mark.parametrize('fluxo', ['adicionar', 'editar', 'planejamento'])
def test_abertura_normal_e_modal(client, cenario_planejamento, fluxo, parcial):
    url = caminho(cenario_planejamento, fluxo, parcial)
    response = client.get(url)
    html, elementos = conferir_html(response, url, parcial, fluxo)
    nomes = [a['name'] for t, a in elementos.nodes if t in ('input', 'select')
             and a.get('name') != 'csrfmiddlewaretoken']
    esperados = {
        'adicionar': ['pessoa', 'codigo_matricula_anac'],
        'editar': ['codigo_matricula_anac'],
        'planejamento': ['data_inicio', 'ata_inicio'],
    }
    assert nomes == esperados[fluxo]
    assert 'resumo-erros' not in html
    assert '<script>' not in html


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
@pytest.mark.parametrize('fluxo', ['adicionar', 'editar', 'planejamento'])
def test_envio_invalido_preserva_contexto_e_exibe_erros(client, cenario_planejamento, fluxo, parcial):
    url = caminho(cenario_planejamento, fluxo, parcial)
    codigo = 'X' * 21 if fluxo == 'editar' else 'MANTIDO'
    response = client.post(url, {'codigo_matricula_anac': codigo})
    html, _ = conferir_html(response, url, parcial, fluxo)
    assert response.context['form'].errors
    assert 'resumo-erros' in html
    assert 'aria-invalid="true"' in html
    for campo in response.context['form']:
        if campo.errors:
            assert f'href="#{campo.id_for_label}"' in html
            assert f'id="{campo.auto_id}_error"' in html
    if fluxo != 'planejamento':
        assert f'value="{codigo}"' in html
    cenario_planejamento['turma'].refresh_from_db()
    assert cenario_planejamento['turma'].situacao == 'PLANEJADA'
    assert MatriculaTurma.objects.count() == 1
    assert cenario_planejamento['matricula'].atribuicao_funcao.dados_discente.codigo_matricula_anac is None


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
@pytest.mark.parametrize('fluxo', ['adicionar', 'editar', 'planejamento'])
def test_envio_pela_action_renderizada_mantem_contrato_e_salvamento(client, cenario_planejamento, fluxo, parcial):
    c = cenario_planejamento
    if fluxo == 'planejamento':
        MatriculaTurma.objects.create(turma=c['turma'], atribuicao_funcao=c['nova'])
        dados = {'data_inicio': '2026-02-01', 'ata_inicio': c['ata'].pk}
    else:
        dados = {'pessoa': c['nova'].pessoa_id, 'codigo_matricula_anac': 'CANAC-TESTE'}
    pagina = client.get(caminho(c, fluxo, parcial))
    action = Elementos(pagina.content.decode()).formulario()['action']
    response = client.post(action, dados)
    assert response.status_code == (200 if parcial else 302)
    if parcial:
        assert response.json() == {'sucesso': True}
    else:
        assert response.url == reverse('gerenciar-turma', kwargs={'pk': c['turma'].pk})
    if fluxo == 'planejamento':
        c['turma'].refresh_from_db()
        assert c['turma'].situacao == 'EM_ANDAMENTO'
        matriculas = list(c['turma'].matriculas.order_by('numero_na_turma'))
        assert [m.atribuicao_funcao.pessoa.nome_completo for m in matriculas] == ['Ana Teste', 'Zuleica Teste']
        assert [m.numero_na_turma for m in matriculas] == [1, 2]
        assert all(m.data_inicio == date(2026, 2, 1) and m.ata_inicio_id == c['ata'].pk for m in matriculas)
    else:
        atribuicao = c['nova'] if fluxo == 'adicionar' else c['matricula'].atribuicao_funcao
        assert MatriculaTurma.objects.filter(turma=c['turma'], atribuicao_funcao=atribuicao).exists()
        atribuicao.dados_discente.refresh_from_db()
        assert atribuicao.dados_discente.codigo_matricula_anac == 'CANAC-TESTE'
        assert MatriculaTurma.objects.count() == (2 if fluxo == 'adicionar' else 1)


@pytest.mark.django_db
@pytest.mark.parametrize('parcial', [False, True])
@pytest.mark.parametrize('com_erro', [False, True])
@pytest.mark.parametrize('tipo', [
    'status_matricula', 'encerrar_turma', 'revisar_aprovacao', 'encerrar_oferta_modulo',
    'toggle_ativo_disciplina', 'toggle_ativo_conteudo_programatico', 'toggle_ativo_modulo',
    'toggle_ativo_submodulo', 'modulo', 'submodulo', 'exclusao',
])
def test_renderizacao_acoes_restantes(cenario_planejamento, tipo, parcial, com_erro):
    from types import SimpleNamespace as NS
    from django import forms
    from django.template.loader import render_to_string
    from django.test import RequestFactory
    from cadastros import forms as cf
    from atribuicao.forms import EditarStatusMatriculaForm, EncerrarTurmaForm, RevisarAprovacaoForm

    c = cenario_planejamento
    classes = {
        'encerrar_oferta_modulo': cf.EncerrarOfertaModuloForm,
        'toggle_ativo_disciplina': cf.DisciplinaToggleAtivoForm,
        'toggle_ativo_conteudo_programatico': cf.ConteudoProgramaticoToggleAtivoForm,
        'toggle_ativo_modulo': cf.ModuloToggleAtivoForm,
        'toggle_ativo_submodulo': cf.SubModuloToggleAtivoForm,
        'modulo': cf.ModuloModelForm, 'submodulo': cf.SubModuloModelForm,
    }
    kwargs = {'data': {}} if com_erro else {}
    if tipo == 'toggle_ativo_disciplina':
        from cadastros.models import Disciplina
        kwargs['instance'] = Disciplina(
            carga_horaria_teorica=0, carga_horaria_pratica=0,
            carga_horaria_programa_de_instrucao=0,
        )
    if tipo == 'status_matricula':
        form = EditarStatusMatriculaForm(matricula=c['matricula'], **kwargs)
    elif tipo == 'encerrar_turma':
        form = EncerrarTurmaForm(turma=c['turma'], **kwargs)
    elif tipo == 'revisar_aprovacao':
        form = RevisarAprovacaoForm(turma=c['turma'], **kwargs)
    else:
        form = classes.get(tipo, forms.Form)(**kwargs)
    if com_erro:
        form.is_valid()
        form.add_error(None, 'Mensagem geral de teste.')
    app = 'atribuicao' if tipo in ('status_matricula', 'encerrar_turma', 'revisar_aprovacao') else 'cadastros'
    nome = 'confirmar_exclusao' if tipo == 'exclusao' else 'form_' + tipo
    fragmento = '_' + nome + '_fragment.html'
    request = RequestFactory().get('/verificacao/', {'parcial': '1'} if parcial else {})
    obj = NS(pk=1, ativo=True, sigla='T', nome='Teste', ordem=1, descricao='Teste',
             disciplina=NS(sigla='D'), disciplina_id=1, modulo=NS(sigla='M', nome='Modulo'), ano_letivo=2026)
    html = render_to_string(app + '/' + (fragmento if parcial else nome + '.html'), {
        'request': request, 'form': form, 'turma': c['turma'], 'matricula': c['matricula'],
        'object': obj, 'url_voltar': '/voltar/', 'csrf_token': 'teste',
    })
    parsed = Elementos(html)
    attrs = parsed.formulario()
    assert attrs['action'] == '/verificacao/' + ('?parcial=1' if parcial else '')
    assert attrs['method'] == 'post'
    assert 'form-modal-crud' in attrs['class']
    assert any(t == 'button' and a.get('class') == 'btn-salvar' for t, a in parsed.nodes)
    assert any(t == 'button' and 'data-fechar-modal-crud' in a for t, a in parsed.nodes) == parcial
    assert ('Mensagem geral de teste.' in html) == com_erro
    ids = [a['id'] for _, a in parsed.nodes if a.get('id')]
    assert len(ids) == len(set(ids))
    for t, a in parsed.nodes:
        if t == 'label':
            assert a['for'] in ids
        for ref in a.get('aria-describedby', '').split():
            assert ref in ids
    assert [a['name'] for t, a in parsed.nodes if t in ('input', 'select', 'textarea')
            and a.get('name') != 'csrfmiddlewaretoken'] == list(form.fields)
