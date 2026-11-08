from html.parser import HTMLParser

import pytest

from cadastros.forms import FormacaoDocenteForm
from cadastros.models import (
    Funcao, Pessoa, VinculoFormal, FormacaoDocente,
    ExperienciaProfissional, HistoricoVinculoFormal, PendenciaCadastro,
)


class HTMLCadastro(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.links = {}
        self.link = None
        self.select = None
        self.options = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.nodes.append((tag, attrs))
        if tag == 'select':
            self.select = attrs['name']
            self.options[self.select] = []
        if tag == 'option' and self.select:
            self.options[self.select].append(attrs)
        if tag == 'a':
            self.link = attrs.get('href')
            self.links[self.link] = ''

    def handle_data(self, value):
        if self.link:
            self.links[self.link] += value

    def handle_endtag(self, tag):
        if tag == 'a':
            self.link = None
        if tag == 'select':
            self.select = None

    def campo(self, name):
        return next(a for t, a in self.nodes if t in ('input', 'select', 'textarea') and a.get('name') == name)

    def conferir_associacoes(self):
        ids = [a['id'] for _, a in self.nodes if a.get('id')]
        assert len(ids) == len(set(ids))
        for tag, attrs in self.nodes:
            if tag == 'label':
                assert attrs.get('for') in ids
            for ref in attrs.get('aria-describedby', '').split():
                assert ref in ids
        for href in self.links:
            if href and href.startswith('#id_'):
                assert href[1:] in ids


@pytest.fixture
def cadastro(db):
    return {
        'DOCENTE': Funcao.objects.create(nome='Docente teste acessibilidade', categoria='DOCENTE'),
        'GESTAO': Funcao.objects.create(nome='Gestao teste acessibilidade', categoria='GESTAO'),
        'DISCENTE': Funcao.objects.create(nome='Discente teste acessibilidade', categoria='DISCENTE'),
        'vinculo': VinculoFormal.objects.create(nome='Vinculo teste acessibilidade'),
    }


def dados_cadastro(cadastro, categoria='DOCENTE'):
    data = {
        'nome_completo': 'Pessoa Teste', 'cpf': '12345678901',
        'data_nascimento': '1990-01-01', 'email': 'pessoa@teste.com', 'telefone': '11999999999',
        'endereco_cep': '12345000', 'endereco_logradouro': 'Rua Teste', 'endereco_numero': '1',
        'endereco_bairro': 'Centro', 'endereco_cidade': 'Cidade', 'endereco_uf': 'SP',
        'funcao': str(cadastro[categoria].pk), 'data_inicio': '2026-01-01', 'situacao': 'ATIVO',
    }
    tipo = FormacaoDocenteForm().fields['tipo_formacao'].choices[1][0]
    for prefix in ('formacao', 'experiencia', 'historico', 'pendencia'):
        data.update({prefix + '-TOTAL_FORMS': '2', prefix + '-INITIAL_FORMS': '0',
                     prefix + '-MIN_NUM_FORMS': '0', prefix + '-MAX_NUM_FORMS': '1000'})
    for i in range(2):
        linhas = {
            'formacao': {'tipo_formacao': tipo, 'curso': f'Curso {i}', 'entidade': f'Entidade {i}',
                         'cidade': 'Cidade', 'uf': 'SP', 'ano_conclusao': '2025'},
            'experiencia': {'organizacao': f'Organizacao {i}', 'cargo': f'Cargo {i}',
                            'data_inicio': '2020-01-01', 'data_fim': ''},
            'historico': {'vinculo_formal': str(cadastro['vinculo'].pk),
                         'data_inicio': '2020-01-01', 'data_fim': '2021-01-01' if i == 0 else ''},
            'pendencia': {'tipo': 'CPF_FISICO', 'descricao': f'Descricao {i}'},
        }
        for prefix, linha in linhas.items():
            data.update({f'{prefix}-{i}-{key}': value for key, value in linha.items()})
    return data


@pytest.mark.django_db
def test_cadastro_inicial_tem_labels_ajuda_e_management_sem_resumo_vazio(client, cadastro):
    response = client.get('/cadastros/novo/')
    assert response.status_code == 200
    html = response.content.decode()
    parsed = HTMLCadastro(html)
    parsed.conferir_associacoes()
    assert 'resumo-erros' not in html
    assert sum(t == 'table' for t, _ in parsed.nodes) == 4
    for campo in response.context['form']:
        if campo.help_text:
            assert campo.auto_id + '_helptext' in parsed.campo(campo.name).get('aria-describedby', '')
    assert 'id="ajuda-consulta-cpf"' in html
    assert 'id="status-consulta-cep"' in html
    assert 'class="btn-salvar"' in html
    for name in response.context['form'].fields:
        assert parsed.campo(name)
    for prefix in ('formacao', 'experiencia', 'historico', 'pendencia'):
        assert parsed.campo(prefix + '-TOTAL_FORMS')['value'] == '1'


@pytest.mark.django_db
def test_erros_no_segundo_registro_dos_quatro_formsets_sao_visiveis_e_associados(client, cadastro):
    data = dados_cadastro(cadastro)
    erros = {
        'formacao-1-ano_conclusao': 'invalido', 'experiencia-1-data_inicio': 'invalida',
        'historico-1-data_inicio': '', 'pendencia-1-tipo': 'INVALIDO',
    }
    data.update(erros)
    response = client.post('/cadastros/novo/', data)
    assert response.status_code == 200
    html = response.content.decode()
    parsed = HTMLCadastro(html)
    parsed.conferir_associacoes()
    assert html.count('class="erro resumo-erros"') == 1
    assert not any(t == 'table' for t, _ in parsed.nodes)
    for name in erros:
        attrs = parsed.campo(name)
        assert attrs['aria-invalid'] == 'true'
        assert attrs['id'] + '_error' in attrs['aria-describedby'].split()
        assert 'Registro 2:' in parsed.links['#' + attrs['id']]
        assert len(parsed.links['#' + attrs['id']]) < 90
    for prefix in ('formacao', 'experiencia', 'historico', 'pendencia'):
        assert parsed.campo(prefix + '-TOTAL_FORMS')['value'] == '2'
    for name in ('formacao-0-curso', 'formacao-1-curso', 'experiencia-0-organizacao',
                 'experiencia-1-organizacao', 'pendencia-0-descricao', 'pendencia-1-descricao'):
        assert parsed.campo(name)['value'] == data[name]
    for name in ('funcao', 'formacao-0-tipo_formacao', 'historico-1-vinculo_formal'):
        assert any('selected' in option and option['value'] == data[name] for option in parsed.options[name])
    assert not Pessoa.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('categoria', ['DOCENTE', 'GESTAO'])
def test_corrigir_envio_invalido_salva_os_dois_registros_da_categoria(client, cadastro, categoria):
    data = dados_cadastro(cadastro, categoria)
    data['email'] = 'email-invalido'
    response = client.post('/cadastros/novo/', data)
    assert response.status_code == 200
    parsed = HTMLCadastro(response.content.decode())
    parsed.conferir_associacoes()
    assert parsed.campo('email')['aria-invalid'] == 'true'
    for prefix, campo in [('formacao', 'curso'), ('experiencia', 'organizacao'),
                          ('historico', 'vinculo_formal'), ('pendencia', 'descricao')]:
        assert parsed.campo(f'{prefix}-1-{campo}')
    assert not Pessoa.objects.exists()
    data['email'] = 'corrigido@teste.com'
    response = client.post('/cadastros/novo/', data)
    assert response.status_code == 302
    pessoa = Pessoa.objects.get(cpf=data['cpf'])
    assert response.url == f'/cadastros/{pessoa.pk}/'
    assert HistoricoVinculoFormal.objects.filter(atribuicao__pessoa=pessoa).count() == 2
    assert PendenciaCadastro.objects.filter(atribuicao__pessoa=pessoa).count() == 2
    assert FormacaoDocente.objects.count() == (2 if categoria == 'DOCENTE' else 0)
    assert ExperienciaProfissional.objects.count() == (2 if categoria == 'GESTAO' else 0)


@pytest.mark.django_db
def test_erro_geral_de_vinculo_obrigatorio_mantem_formacoes_e_mensagem(client, cadastro):
    data = dados_cadastro(cadastro)
    data['historico-TOTAL_FORMS'] = '0'
    response = client.post('/cadastros/novo/', data)
    assert response.status_code == 200
    html = response.content.decode()
    parsed = HTMLCadastro(html)
    parsed.conferir_associacoes()
    assert 'É obrigatório informar ao menos um Histórico' in html
    assert parsed.campo('formacao-1-curso')['value'] == 'Curso 1'
    assert not Pessoa.objects.exists()


@pytest.mark.django_db
def test_management_form_ausente_tem_erro_geral_legivel_sem_quebrar_pagina(client, cadastro):
    data = dados_cadastro(cadastro)
    del data['formacao-TOTAL_FORMS']
    response = client.post('/cadastros/novo/', data)
    assert response.status_code == 200
    html = response.content.decode()
    HTMLCadastro(html).conferir_associacoes()
    assert response.context['formacao_formset'].non_form_errors()
    assert 'class="erro resumo-erros"' in html
    assert not Pessoa.objects.exists()
