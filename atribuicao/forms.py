"""
atribuicao/forms.py
"""

from django import forms

from cadastros.models import Pessoa, Ata, FinalidadeAta, CategoriaModulo
from cadastros.services import ObterOuCriarAtribuicaoDiscenteService
from .models import MatriculaTurma
from .services import atribuicoes_elegiveis_para_turma_regular


class AdicionarMatriculaTurmaForm(forms.ModelForm):
    """
    Popup "+ Adicionar Aluno" (docs/37, seção 4.1). Nenhum campo do próprio
    Model no formulário (fields=[]) — 'pessoa' e 'codigo_matricula_anac' são
    resolvidos aqui, e a AtribuicaoFuncao correspondente é obtida/criada via
    ObterOuCriarAtribuicaoDiscenteService (cadastros) dentro de save().

    Dropdown de Pessoa depende do tipo da Turma: Extracurricular aceita
    qualquer Pessoa; Turma regular só aceita Discente ATIVO "Aguardando
    Atribuição/Turma" (ver atribuicoes_elegiveis_para_turma_regular).
    """
    pessoa = forms.ModelChoiceField(queryset=Pessoa.objects.none(), label="Aluno")
    codigo_matricula_anac = forms.CharField(max_length=20, required=False, label="Código de Matrícula ANAC")

    class Meta:
        model = MatriculaTurma
        fields = []

    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop('turma')
        super().__init__(*args, **kwargs)

        if self.turma.oferta_modulo.modulo.categoria == CategoriaModulo.EXTRACURRICULAR:
            self.fields['pessoa'].queryset = Pessoa.objects.all().order_by('nome_completo')
        else:
            elegiveis = atribuicoes_elegiveis_para_turma_regular()
            self.fields['pessoa'].queryset = Pessoa.objects.filter(
                id__in=elegiveis.values_list('pessoa_id', flat=True)
            ).order_by('nome_completo')

    def clean_pessoa(self):
        pessoa = self.cleaned_data['pessoa']
        if MatriculaTurma.objects.filter(turma=self.turma, atribuicao_funcao__pessoa=pessoa).exists():
            raise forms.ValidationError("Esta Pessoa já está matriculada nesta Turma.")
        return pessoa

    def save(self, commit=True):
        from django.utils import timezone

        pessoa = self.cleaned_data['pessoa']
        canac = self.cleaned_data.get('codigo_matricula_anac')

        atribuicao = ObterOuCriarAtribuicaoDiscenteService().executar(pessoa, timezone.now().date())
        if canac and not atribuicao.dados_discente.codigo_matricula_anac:
            atribuicao.dados_discente.codigo_matricula_anac = canac
            atribuicao.dados_discente.save()

        self.instance.atribuicao_funcao = atribuicao
        self.instance.turma = self.turma
        return super().save(commit=commit)


class EditarMatriculaTurmaForm(forms.ModelForm):
    """
    Popup "Editar/CRU" enquanto a Turma está PLANEJADA (docs/37, seção 4.1) —
    só corrige o Código de Matrícula ANAC (que mora em DadosDiscente, não em
    MatriculaTurma). A edição de 'status' (Em Andamento) é um Form separado,
    ainda não implementado nesta etapa.
    """
    codigo_matricula_anac = forms.CharField(max_length=20, required=False, label="Código de Matrícula ANAC")

    class Meta:
        model = MatriculaTurma
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo_matricula_anac'].initial = (
            self.instance.atribuicao_funcao.dados_discente.codigo_matricula_anac
        )

    def save(self, commit=True):
        dados_discente = self.instance.atribuicao_funcao.dados_discente
        dados_discente.codigo_matricula_anac = self.cleaned_data.get('codigo_matricula_anac') or None
        dados_discente.save()
        return self.instance


class FinalizarPlanejamentoForm(forms.Form):
    """Popup do botão "Finalizar Planejamento" (docs/37, seção 4.2)."""
    data_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label="Data de Início"
    )
    ata_inicio = forms.ModelChoiceField(
        queryset=Ata.objects.filter(finalidade=FinalidadeAta.INICIO_VINCULO).order_by('-data'),
        label="Ata de Início de Vínculo",
        help_text="A Ata precisa já existir — cadastre em /cadastros/atas/ antes, se necessário.",
    )
