"""
cadastros/forms.py

Form de entrada para a Template View de cadastro (Etapa 7.3/7.4c - formulário
completo, único, com dropdown de Funcao; JavaScript, na Etapa 7.4d, mostra/esconde
os blocos de campos conforme a categoria da Funcao escolhida).

Estrutura:
    CadastrarPessoaForm            — campos fixos: Pessoa (completo), Funcao,
                                     AtribuicaoFuncao, e os campos de DadosDiscente
                                     (aplicáveis só quando a Funcao é de categoria Discente).
    FormacaoDocenteForm            — 1 linha de Graduação/Formação/Aperfeiçoamento (Docente),
                                     usada só no cadastro INICIAL (Formset).
    ExperienciaProfissionalForm    — 1 linha de Experiência Profissional (Gestão),
                                     usada só no cadastro INICIAL (Formset).
    HistoricoVinculoFormalForm     — 1 linha de Vínculo Formal (Docente ou Gestão),
                                     usada só no cadastro INICIAL (Formset).
    PendenciaCadastroForm          — 1 linha de Pendência de documentação (universal,
                                     qualquer categoria — Discente, Docente ou Gestão).

    ModelForms do CRUD independente (piloto docs/21), usados FORA do cadastro
    inicial — depois que a Pessoa/AtribuicaoFuncao já existe:
    FormacaoDocenteModelForm             — Adicionar/Editar uma Formação.
    HistoricoVinculoFormalModelForm      — Adicionar um novo período de Vínculo Formal.
    EncerrarHistoricoVinculoFormalForm   — Encerrar um período já existente (só
                                           data_fim + observacao — nunca reabre
                                           vinculo_formal/data_inicio; não há Delete
                                           para esta entidade, só encerramento).
    ExperienciaProfissionalModelForm     — Adicionar/Editar uma Experiência
                                           Profissional (Delete real permitido,
                                           diferente de Vínculo Formal).

Os 4 Forms de linha (Formação/Experiência/Histórico/Pendência acima) viram Formsets
(forms.formset_factory) — permitem 0 a N linhas no cadastro inicial, cada uma
repetindo os mesmos campos, com JavaScript controlando quantas aparecem na tela
(Etapa 7.4d). Usar Form comum (não ModelForm) ali: no momento do cadastro inicial,
o objeto pai (DadosDocente/AtribuicaoFuncao) ainda não existe — o Service é quem
cria os Models de verdade a partir dos dicts já validados pelo Form.

Todos os campos de linha (Formação/Experiência/Histórico) são `required=False`
de propósito, para que a linha `extra=1` do Formset possa ser enviada em branco
sem gerar erro quando o usuário não quer adicionar nenhuma. Isso abre uma brecha
de preenchimento parcial (ex: Curso preenchido, Ano de conclusão vazio) que só
seria barrada no banco (IntegrityError, pouco amigável) sem um `clean()`
customizado — daí o `clean()` em cada Form abaixo que tem campos realmente
obrigatórios no Model. Cada `clean()` usa o mesmo campo "sinal" que
`views.py::_CAMPO_PREENCHIDO` já usa para decidir se uma linha foi preenchida
de verdade: se o campo sinal estiver preenchido, os demais campos obrigatórios
do Model passam a ser exigidos também. `PendenciaCadastroForm` não precisa de
`clean()`: seu único outro campo (`descricao`) já é opcional de verdade no Model.
Bug descoberto em teste manual em 31/08/2026 (ver docs/17), corrigido aqui.

Nos ModelForms do CRUD independente, campos de data usam sempre
`forms.DateInput(attrs={'type': 'date'})` (mesmo padrão dos outros Forms do
projeto) — sem isso, o Django usa um <input type="text"> comum, sem o
calendário do navegador. Campos de texto longo (Textarea) recebem
`style="width:100%; box-sizing:border-box;"` — sem isso, a largura padrão do
navegador para <textarea> (baseada no atributo `cols`) pode ultrapassar a
largura da caixa do popup/modal. Bug descoberto em teste manual em 01/09/2026.
"""

from django import forms

from .models import (
    Funcao, VinculoFormal, TipoFormacaoDocente, TipoPendencia,
    Sexo, EstadoCivil, RacaCor, FormacaoDocente, HistoricoVinculoFormal,
    ExperienciaProfissional,
)


class CadastrarPessoaForm(forms.Form):
    # --- Pessoa: dados básicos ---
    nome_completo = forms.CharField(max_length=200, label="Nome completo")
    cpf = forms.CharField(max_length=11, label="CPF")
    data_nascimento = forms.DateField(
        label="Data de nascimento", widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(label="E-mail")
    telefone = forms.CharField(max_length=20, label="Telefone")

    # --- Pessoa: identificadores específicos ---
    registro_matricula = forms.CharField(max_length=20, required=False, label="RM")
    registro_aluno = forms.CharField(max_length=20, required=False, label="RA")
    codigo_anac = forms.CharField(max_length=20, required=False, label="CANAC")

    # --- Pessoa: identificação ampliada (FE 007 / FE 008) ---
    sexo = forms.ChoiceField(choices=[('', '---------')] + list(Sexo.choices), required=False, label="Sexo")
    identidade = forms.CharField(max_length=20, required=False, label="Identidade (RG)")
    data_emissao_identidade = forms.DateField(
        required=False, label="Data de emissão", widget=forms.DateInput(attrs={'type': 'date'})
    )
    orgao_expedidor_identidade = forms.CharField(max_length=20, required=False, label="Órgão expedidor")
    naturalidade = forms.CharField(max_length=100, required=False, label="Naturalidade")
    uf_naturalidade = forms.CharField(max_length=2, required=False, label="UF de naturalidade")
    nacionalidade = forms.CharField(max_length=100, required=False, label="Nacionalidade")
    filiacao_1 = forms.CharField(max_length=200, required=False, label="Filiação 1")
    filiacao_2 = forms.CharField(max_length=200, required=False, label="Filiação 2")
    nivel_instrucao = forms.CharField(max_length=100, required=False, label="Nível de instrução")
    estado_civil = forms.ChoiceField(choices=[('', '---------')] + list(EstadoCivil.choices), required=False, label="Estado civil")
    raca_cor = forms.ChoiceField(choices=[('', '---------')] + list(RacaCor.choices), required=False, label="Raça/Cor")

    # --- Pessoa: endereço ---
    endereco_cep = forms.CharField(max_length=8, label="CEP")
    endereco_logradouro = forms.CharField(max_length=200, label="Logradouro")
    endereco_numero = forms.CharField(max_length=10, label="Numero")
    endereco_complemento = forms.CharField(max_length=100, required=False, label="Complemento")
    endereco_bairro = forms.CharField(max_length=100, label="Bairro")
    endereco_cidade = forms.CharField(max_length=100, label="Cidade")
    endereco_uf = forms.CharField(max_length=2, label="UF")

    # --- Funcao / AtribuicaoFuncao ---
    funcao = forms.ModelChoiceField(queryset=Funcao.objects.all(), label="Funcao")
    data_inicio = forms.DateField(
        label="Data de inicio", widget=forms.DateInput(attrs={'type': 'date'})
    )
    situacao = forms.CharField(max_length=30, initial="ATIVO", label="Situacao")

    # --- DadosDiscente (só relevante quando Funcao.categoria == DISCENTE) ---
    codigo_matricula_anac = forms.CharField(
        max_length=20, required=False, label="Código de Matrícula ANAC"
    )
    passaporte = forms.CharField(max_length=20, required=False, label="Nº do Passaporte")
    autorizacao_permanencia = forms.CharField(
        max_length=50, required=False, label="Autorização de Permanência"
    )
    contato_emergencia_nome = forms.CharField(
        max_length=200, required=False, label="Contato de emergência - Nome"
    )
    contato_emergencia_parentesco = forms.CharField(
        max_length=50, required=False, label="Contato de emergência - Parentesco"
    )
    contato_emergencia_telefone = forms.CharField(
        max_length=20, required=False, label="Contato de emergência - Telefone"
    )
    contato_emergencia_endereco = forms.CharField(
        max_length=300, required=False, label="Contato de emergência - Endereço"
    )
    responsavel_nome = forms.CharField(
        max_length=200, required=False, label="Responsável legal - Nome"
    )
    responsavel_endereco = forms.CharField(
        max_length=300, required=False, label="Responsável legal - Endereço"
    )
    responsavel_identidade = forms.CharField(
        max_length=20, required=False, label="Responsável legal - Identidade"
    )
    responsavel_orgao_expedidor = forms.CharField(
        max_length=20, required=False, label="Responsável legal - Órgão expedidor"
    )
    responsavel_data_emissao = forms.DateField(
        required=False, label="Responsável legal - Data de emissão",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    responsavel_qualificacao = forms.CharField(
        max_length=50, required=False, label="Responsável legal - Qualificação (pai/mãe/tutor)"
    )


class FormacaoDocenteForm(forms.Form):
    """1 linha de Graduação/Formação Profissional/Aperfeiçoamento (FE 008, seções 3-5)."""
    tipo_formacao = forms.ChoiceField(
        choices=[('', '---------')] + list(TipoFormacaoDocente.choices),
        required=False, label="Tipo"
    )
    curso = forms.CharField(max_length=200, required=False, label="Curso")
    entidade = forms.CharField(max_length=200, required=False, label="Entidade")
    cidade = forms.CharField(max_length=100, required=False, label="Cidade")
    uf = forms.CharField(max_length=2, required=False, label="UF")
    ano_conclusao = forms.IntegerField(required=False, label="Ano de conclusão")

    def clean(self):
        cleaned_data = super().clean()
        # 'curso' é o mesmo campo-sinal usado em views.py::_CAMPO_PREENCHIDO
        # para decidir se esta linha do Formset foi preenchida de verdade.
        if cleaned_data.get('curso'):
            campos_obrigatorios = ['tipo_formacao', 'entidade', 'cidade', 'uf', 'ano_conclusao']
            for campo in campos_obrigatorios:
                if not cleaned_data.get(campo):
                    self.add_error(campo, "Obrigatório quando o Curso é preenchido.")
        return cleaned_data


class ExperienciaProfissionalForm(forms.Form):
    """1 linha de Experiência Profissional (FOP 402, só categoria Gestão), usada só no cadastro INICIAL (Formset)."""
    organizacao = forms.CharField(max_length=200, required=False, label="Organização")
    cargo = forms.CharField(max_length=100, required=False, label="Cargo")
    data_inicio = forms.DateField(
        required=False, label="Data de início", widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False, label="Data de fim", widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()
        # 'organizacao' é o mesmo campo-sinal usado em views.py::_CAMPO_PREENCHIDO.
        if cleaned_data.get('organizacao'):
            campos_obrigatorios = ['cargo', 'data_inicio']
            for campo in campos_obrigatorios:
                if not cleaned_data.get(campo):
                    self.add_error(campo, "Obrigatório quando a Organização é preenchida.")
        return cleaned_data


class HistoricoVinculoFormalForm(forms.Form):
    """1 linha de Vínculo Formal (Docente ou Gestão — nunca Discente), usada só no cadastro INICIAL (Formset)."""
    vinculo_formal = forms.ModelChoiceField(
        queryset=VinculoFormal.objects.all(), required=False, label="Vínculo Formal"
    )
    data_inicio = forms.DateField(
        required=False, label="Data de início", widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False, label="Data de fim", widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()
        # 'vinculo_formal' é o mesmo campo-sinal usado em views.py::_CAMPO_PREENCHIDO.
        if cleaned_data.get('vinculo_formal') and not cleaned_data.get('data_inicio'):
            self.add_error('data_inicio', "Obrigatório quando o Vínculo Formal é preenchido.")
        return cleaned_data


class PendenciaCadastroForm(forms.Form):
    """
    1 linha de Pendência de documentação — universal, qualquer categoria.
    Sem `clean()` customizado: diferente dos 3 Forms acima, o único outro
    campo além do sinal ('tipo') é 'descricao', que já é opcional de verdade
    no Model (`blank=True`) — não existe combinação parcial inválida aqui.
    """
    tipo = forms.ChoiceField(
        choices=[('', '---------')] + list(TipoPendencia.choices),
        required=False, label="Tipo"
    )
    descricao = forms.CharField(
        max_length=200, required=False, label="Descrição (detalhe, usar sobretudo em 'Outro')"
    )


class FormacaoDocenteModelForm(forms.ModelForm):
    """
    ModelForm para o CRUD independente de FormacaoDocente (Create/Update),
    usado fora do fluxo de cadastro inicial — depois que o Docente já existe.
    Primeiro passo da migração de arquitetura descrita em docs/21: o pai
    (DadosDocente) é resolvido pela View a partir da URL, nunca por um campo
    enviado pelo navegador — 'dados_docente' fica de fora de `fields`, de
    propósito, para não poder ser manipulado pelo POST.
    """
    class Meta:
        model = FormacaoDocente
        fields = ['tipo_formacao', 'curso', 'entidade', 'cidade', 'uf', 'ano_conclusao']


_WIDGET_OBSERVACAO = forms.Textarea(attrs={
    'rows': 3,
    'style': 'width:100%; box-sizing:border-box;',
})


class HistoricoVinculoFormalModelForm(forms.ModelForm):
    """
    ModelForm para adicionar um NOVO período de Vínculo Formal a uma
    AtribuicaoFuncao já existente (Docente ou Gestão) — ex: quando a entidade
    contratante muda (FAPETI até 2026, FUSSUSS a partir de 2026). 'atribuicao'
    fica de fora de `fields`: é resolvida pela View a partir da URL.
    """
    class Meta:
        model = HistoricoVinculoFormal
        fields = ['vinculo_formal', 'data_inicio', 'data_fim', 'observacao']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': _WIDGET_OBSERVACAO,
        }


class EncerrarHistoricoVinculoFormalForm(forms.ModelForm):
    """
    ModelForm restrito para ENCERRAR um período de Vínculo Formal já
    existente — nunca Delete, só preencher 'data_fim' (mais 'observacao'
    para registrar erro de cadastro ou contexto do encerramento). 'vinculo_
    formal' e 'data_inicio' ficam de fora de `fields` de propósito: uma vez
    criado, esse período não pode ser reaberto/reescrito, só encerrado.
    """
    class Meta:
        model = HistoricoVinculoFormal
        fields = ['data_fim', 'observacao']
        widgets = {
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': _WIDGET_OBSERVACAO,
        }


class ExperienciaProfissionalModelForm(forms.ModelForm):
    """
    ModelForm para o CRUD independente de ExperienciaProfissional (Create/
    Update/Delete) — diferente de HistoricoVinculoFormal, esta entidade
    permite exclusão real (não há regra de negócio de "nunca apagar" aqui).
    'atribuicao' fica de fora de `fields`: é resolvida pela View a partir
    da URL.
    """
    class Meta:
        model = ExperienciaProfissional
        fields = ['organizacao', 'cargo', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }


# Formsets — "fábricas" que embrulham cada Form acima, permitindo 0-N linhas.
# extra=1: a tela já nasce com 1 linha em branco visível (decisão da Etapa 7.3).
# Definidos aqui, uma vez só, para serem reaproveitados igual em views.py (GET e POST).
FormacaoDocenteFormSet = forms.formset_factory(FormacaoDocenteForm, extra=1)
ExperienciaProfissionalFormSet = forms.formset_factory(ExperienciaProfissionalForm, extra=1)
HistoricoVinculoFormalFormSet = forms.formset_factory(HistoricoVinculoFormalForm, extra=1)
PendenciaCadastroFormSet = forms.formset_factory(PendenciaCadastroForm, extra=1)
