from html.parser import HTMLParser

import pytest
from django import forms
from django.template.loader import render_to_string


class Marcacao(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.parents = []
        self.stack = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))
        self.parents.append(tuple(self.stack))
        if tag not in ('input', 'br', 'hr', 'img', 'meta', 'link'):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]


@pytest.mark.parametrize('widget', [forms.TextInput, forms.Select, forms.RadioSelect])
@pytest.mark.parametrize('required', [False, True])
def test_rotulo_nativo_com_asterisco_e_ajuda_apos_controle(widget, required):
    class Formulario(forms.Form):
        campo = forms.ChoiceField(
            label='Campo de teste', choices=[('', '---------'), ('1', 'Primeira opção')],
            widget=widget, required=required, help_text='Ajuda de teste.',
        )

    form = Formulario()
    html = render_to_string('includes/campo_formulario.html', {'campo': form['campo']})
    parsed = Marcacao(html)
    indicadores = [(i, a) for i, (t, a) in enumerate(parsed.nodes) if t == 'abbr']
    assert len(indicadores) == int(required)
    for i, attrs in indicadores:
        assert attrs['title'] == 'Obrigatório'
        assert ('legend' if widget == forms.RadioSelect else 'label') in parsed.parents[i]
    controles = [(i, a) for i, (t, a) in enumerate(parsed.nodes) if t in ('input', 'select')]
    ajuda = next(i for i, (_, a) in enumerate(parsed.nodes) if a.get('id') == 'id_campo_helptext')
    assert all(i < ajuda for i, _ in controles)
    assert all(('required' in attrs) == required for _, attrs in controles)
    ids = [a['id'] for _, a in parsed.nodes if a.get('id')]
    for tag, attrs in parsed.nodes:
        if tag == 'label':
            assert attrs['for'] in ids
        for ref in attrs.get('aria-describedby', '').split():
            assert ref in ids


def test_campo_oculto_nao_recebe_indicador_ou_instrucoes():
    class Formulario(forms.Form):
        campo = forms.CharField(widget=forms.HiddenInput)

    form = Formulario()
    html = render_to_string('includes/campo_formulario.html', {'campo': form['campo']})
    assert '<abbr' not in html
    assert 'type="hidden"' in html
    assert 'instrucoes-formulario' not in render_to_string(
        'includes/instrucoes_obrigatoriedade.html', {'form': form},
    )


@pytest.mark.parametrize('required', [False, True])
def test_explicacao_aparece_uma_vez_no_inicio_sem_exigir_repeticao_por_campo(required):
    class Formulario(forms.Form):
        primeiro = forms.CharField(required=required)
        segundo = forms.CharField(required=required)

    html = render_to_string('includes/resumo_erros_formulario.html', {'form': Formulario()})
    assert html.count('class="instrucoes-formulario"') == int(required)
    assert 'resumo-erros' not in html


def test_rotulo_continua_escapado_e_erro_associado_ao_campo():
    class Formulario(forms.Form):
        campo = forms.CharField(label='<script>rótulo</script>', help_text='Ajuda.')

    form = Formulario(data={})
    html = render_to_string('includes/campo_formulario.html', {'campo': form['campo']})
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'aria-invalid="true"' in html
    assert 'id="id_campo_error"' in html
    assert 'aria-describedby="id_campo_helptext id_campo_error"' in html


def test_resumo_de_grupo_invalido_aponta_para_opcao_focavel():
    class Formulario(forms.Form):
        campo = forms.ChoiceField(widget=forms.RadioSelect, choices=[('1', 'Primeira opção')])

    form = Formulario(data={})
    html = render_to_string('includes/resumo_erros_formulario.html', {'form': form})
    campo = render_to_string('includes/campo_formulario.html', {'campo': form['campo']})
    assert 'href="#id_campo_0"' in html
    assert 'id="id_campo_0"' in campo


def test_resumo_de_erro_oculto_nao_cria_link_inutil():
    class Formulario(forms.Form):
        campo = forms.CharField(widget=forms.HiddenInput)

    html = render_to_string('includes/resumo_erros_formulario.html', {'form': Formulario(data={})})
    assert 'href="#id_campo"' not in html
