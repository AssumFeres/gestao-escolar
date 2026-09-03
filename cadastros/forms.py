"""
cadastros/forms.py

(ver documentação completa no cabeçalho de views.py/docs do projeto)

`data_nascimento` (CadastrarPessoaForm/EditarPessoaForm):
- `min` fixo em 1900-01-01, `max` calculado dinamicamente como a data de HOJE
  a cada instância do Form (não um valor fixo como "2070-12-31") — trava no
  próprio navegador contra ano digitado errado (bug real de teste manual em
  02/09/2026, "12121-12-03") e contra data de nascimento no futuro.
- `clean_data_nascimento()` é a validação AUTORITATIVA (o `max` do HTML é só
  uma trava de navegador, sempre contornável) — rejeita Data de Nascimento
  igual a hoje ou no futuro, com uma mensagem de erro clara. Regra confirmada
  em 02/09/2026: ninguém nasce no futuro, então essa combinação é sempre
  inválida, não uma advertência.

Passaporte/Autorização de Permanência (03/09/2026): campos de Pessoa desde a
auditoria de campos FE 007/FE 008/FOP 402 — visíveis na Identificação Ampliada,
para qualquer categoria (Docente também usa essa documentação, não é exclusiva
de Discente).
"""

from datetime import date

from django import forms

from .models import (
    Funcao, VinculoFormal, TipoFormacaoDocente, TipoPendencia,
    Sexo, EstadoCivil, RacaCor, FormacaoDocente, HistoricoVinculoFormal,
    ExperienciaProfissional, PendenciaCadastro, AtribuicaoFuncao,
    RequisitoContratacao, Pessoa,
)


def _validar_data_nascimento_nao_futura(valor):
    """
    Compartilhada por CadastrarPessoaForm e EditarPessoaForm — Data de
    Nascimento igual a hoje ou no futuro é sempre inválida (ninguém nasce
    no futuro). Levanta ValidationError se a regra for violada.
    """
    if valor and valor >= date.today():
        raise forms.ValidationError(
            "Data de nascimento inválida: não pode ser hoje nem uma data futura."
        )
    return valor


class CadastrarPessoaForm(forms.Form):
    # --- Pessoa: dados básicos ---
    nome_completo = forms.CharField(max_length=200, label="Nome completo")
    cpf = forms.CharField(max_length=11, label="CPF")
    data_nascimento = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(attrs={'type': 'date', 'min': '1900-01-01'})
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

    # --- Pessoa: Título de Eleitor / E-mail 2 / Telefone 2 / Passaporte (aprovados
    # na auditoria de campos de 03/09/2026 — ver docs/28) ---
    titulo_eleitor = forms.CharField(max_length=12, required=False, label="Título de Eleitor")
    zona_eleitoral = forms.CharField(max_length=3, required=False, label="Zona Eleitoral")
    secao_eleitoral = forms.CharField(max_length=4, required=False, label="Seção Eleitoral")
    email_2 = forms.EmailField(required=False, label="E-mail 2")
    telefone_2 = forms.CharField(max_length=20, required=False, label="Telefone 2 / Celular")

    # Passaporte/Autorização de Permanência: campo de Pessoa desde 03/09/2026 (visível
    # para qualquer categoria na Identificação Ampliada, não só Discente).
    passaporte = forms.CharField(max_length=20, required=False, label="Nº do Passaporte")
    autorizacao_permanencia = forms.CharField(
        max_length=50, required=False, label="Autorização de Permanência"
    )

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

    # --- AtribuicaoFuncao: Requisitos de Contratação (RBAC 141), todos exceto
    # Discente. Coletados já no cadastro inicial (decisão de 02/09/2026).
    requisito_contratacao = forms.ChoiceField(
        choices=RequisitoContratacao.choices, required=False,
        widget=forms.RadioSelect(), label="Requisito de Contratação"
    )
    documento_comprobatorio = forms.CharField(
        max_length=200, required=False, label="Documento comprobatório"
    )

    # --- DadosDiscente (só relevante quando Funcao.categoria == DISCENTE) ---
    codigo_matricula_anac = forms.CharField(
        max_length=20, required=False, label="Código de Matrícula ANAC"
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 'max' calculado a cada instância (não um valor fixo) — sempre a
        # data de hoje, real, no momento em que o formulário é exibido.
        self.fields['data_nascimento'].widget.attrs['max'] = date.today().isoformat()

    def clean_data_nascimento(self):
        return _validar_data_nascimento_nao_futura(self.cleaned_data.get('data_nascimento'))


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
        if cleaned_data.get('vinculo_formal') and not cleaned_data.get('data_inicio'):
            self.add_error('data_inicio', "Obrigatório quando o Vínculo Formal é preenchido.")
        return cleaned_data


class PendenciaCadastroForm(forms.Form):
    """1 linha de Pendência de documentação — universal, qualquer categoria."""
    tipo = forms.ChoiceField(
        choices=[('', '---------')] + list(TipoPendencia.choices),
        required=False, label="Tipo"
    )
    descricao = forms.CharField(
        max_length=200, required=False, label="Descrição (detalhe, usar sobretudo em 'Outro')"
    )


class EditarPessoaForm(forms.ModelForm):
    """
    Edita os campos COMUNS da Pessoa (identificação + endereço) — qualquer
    categoria. 'cpf' fora (imutável), Função fora (item futuro), campos de
    DadosDiscente fora (Discente ainda sem CRUD próprio). Pessoa nunca é
    excluída — só Create/Read/Update.
    """
    class Meta:
        model = Pessoa
        fields = [
            'nome_completo', 'data_nascimento', 'email', 'email_2', 'telefone', 'telefone_2',
            'registro_matricula', 'registro_aluno', 'codigo_anac',
            'sexo', 'identidade', 'data_emissao_identidade', 'orgao_expedidor_identidade',
            'naturalidade', 'uf_naturalidade', 'nacionalidade',
            'filiacao_1', 'filiacao_2', 'nivel_instrucao', 'estado_civil', 'raca_cor',
            'titulo_eleitor', 'zona_eleitoral', 'secao_eleitoral',
            'passaporte', 'autorizacao_permanencia',
            'endereco_cep', 'endereco_logradouro', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cidade', 'endereco_uf',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'min': '1900-01-01'}),
            'data_emissao_identidade': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].widget.attrs['max'] = date.today().isoformat()

    def clean_data_nascimento(self):
        return _validar_data_nascimento_nao_futura(self.cleaned_data.get('data_nascimento'))


class FormacaoDocenteModelForm(forms.ModelForm):
    """ModelForm para o CRUD independente de FormacaoDocente (Create/Update)."""
    class Meta:
        model = FormacaoDocente
        fields = ['tipo_formacao', 'curso', 'entidade', 'cidade', 'uf', 'ano_conclusao']


_WIDGET_OBSERVACAO = forms.Textarea(attrs={
    'rows': 3,
    'style': 'width:100%; box-sizing:border-box;',
})


class HistoricoVinculoFormalModelForm(forms.ModelForm):
    """ModelForm para adicionar um NOVO período de Vínculo Formal a uma AtribuicaoFuncao já existente."""
    class Meta:
        model = HistoricoVinculoFormal
        fields = ['vinculo_formal', 'data_inicio', 'data_fim', 'observacao']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': _WIDGET_OBSERVACAO,
        }


class EncerrarHistoricoVinculoFormalForm(forms.ModelForm):
    """ModelForm restrito para ENCERRAR um período de Vínculo Formal já existente — nunca Delete."""
    class Meta:
        model = HistoricoVinculoFormal
        fields = ['data_fim', 'observacao']
        widgets = {
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': _WIDGET_OBSERVACAO,
        }


class ExperienciaProfissionalModelForm(forms.ModelForm):
    """ModelForm para o CRUD independente de ExperienciaProfissional (Create/Update/Delete)."""
    class Meta:
        model = ExperienciaProfissional
        fields = ['organizacao', 'cargo', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }


class PendenciaCadastroModelForm(forms.ModelForm):
    """ModelForm para CRIAR uma nova PendenciaCadastro — só 'tipo' e 'descricao'."""
    class Meta:
        model = PendenciaCadastro
        fields = ['tipo', 'descricao']


class EditarPendenciaCadastroForm(forms.ModelForm):
    """ModelForm para EDITAR uma PendenciaCadastro já existente, incluindo marcar como resolvida."""
    class Meta:
        model = PendenciaCadastro
        fields = ['tipo', 'descricao', 'resolvida']


class EditarRequisitoContratacaoForm(forms.ModelForm):
    """
    Edita os Requisitos de Contratação (RBAC 141) de uma AtribuicaoFuncao já
    existente — Docente ou Gestão. Usado fora do cadastro inicial, para
    corrigir/completar depois pela tela de detalhe.
    """
    class Meta:
        model = AtribuicaoFuncao
        fields = ['requisito_contratacao', 'documento_comprobatorio']
        widgets = {
            'requisito_contratacao': forms.RadioSelect(),
        }


# Formsets
FormacaoDocenteFormSet = forms.formset_factory(FormacaoDocenteForm, extra=1)
ExperienciaProfissionalFormSet = forms.formset_factory(ExperienciaProfissionalForm, extra=1)
HistoricoVinculoFormalFormSet = forms.formset_factory(HistoricoVinculoFormalForm, extra=1)
PendenciaCadastroFormSet = forms.formset_factory(PendenciaCadastroForm, extra=1)
