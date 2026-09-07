"""
atribuicao/forms.py
"""

from django import forms

from cadastros.models import Pessoa, Ata, FinalidadeAta, CategoriaModulo, Turma, SituacaoTurma
from cadastros.services import ObterOuCriarAtribuicaoDiscenteService
from .models import MatriculaTurma, StatusMatriculaTurma, MotivoSaida
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
        from django.db.models import Max
        from django.utils import timezone

        pessoa = self.cleaned_data['pessoa']
        canac = self.cleaned_data.get('codigo_matricula_anac')

        atribuicao = ObterOuCriarAtribuicaoDiscenteService().executar(pessoa, timezone.now().date())
        if canac and not atribuicao.dados_discente.codigo_matricula_anac:
            atribuicao.dados_discente.codigo_matricula_anac = canac
            atribuicao.dados_discente.save()

        self.instance.atribuicao_funcao = atribuicao
        self.instance.turma = self.turma

        # Turma já EM_ANDAMENTO (aluno relocado entrando, ou Extracurricular novo):
        # numero_na_turma = MAX+1 desta Turma, e ganha data_inicio na hora. Enquanto
        # PLANEJADA, isso fica para "Finalizar Planejamento" (docs/37, seção 4.3).
        if self.turma.situacao != SituacaoTurma.PLANEJADA:
            max_atual = MatriculaTurma.objects.filter(turma=self.turma).aggregate(
                Max('numero_na_turma')
            )['numero_na_turma__max'] or 0
            self.instance.numero_na_turma = max_atual + 1
            self.instance.data_inicio = timezone.now().date()

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



class EditarStatusMatriculaForm(forms.Form):
    """
    Popup "Editar/CRU" enquanto a Turma está EM_ANDAMENTO (docs/37, seção 4.3)
    — só chamado quando matricula.status ainda é CURSANDO. Campos exigidos
    variam por 'status' escolhido, validados em clean() (sem JS condicional
    nesta etapa — todos os campos aparecem sempre, com texto explicando
    quando cada um se aplica).
    """
    status = forms.ChoiceField(
        choices=[
            (StatusMatriculaTurma.RELOCADO, 'Relocado'),
            (StatusMatriculaTurma.REPROVADO, 'Reprovado'),
            (StatusMatriculaTurma.TRANSFERIDO, 'Transferido'),
            (StatusMatriculaTurma.MATRICULA_EXCLUIDA, 'Matrícula Excluída'),
        ],
        label="Novo Status",
    )
    turma_destino = forms.ModelChoiceField(
        queryset=Turma.objects.none(), required=False,
        label="Turma de destino", help_text="Obrigatório só para Relocado.",
    )
    motivo_saida = forms.ChoiceField(
        choices=[('', '---------')] + list(MotivoSaida.choices), required=False,
        label="Motivo da saída", help_text="Obrigatório só para Transferido.",
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), required=False,
        label="Data de Fim", help_text="Obrigatório para Reprovado/Transferido/Matrícula Excluída.",
    )
    ata_encerramento = forms.ModelChoiceField(
        queryset=Ata.objects.filter(finalidade=FinalidadeAta.TERMINO_VINCULO).order_by('-data'),
        required=False, label="Ata de Término de Vínculo",
        help_text="Obrigatório para Reprovado/Transferido/Matrícula Excluída — a Ata precisa já existir.",
    )

    def __init__(self, *args, **kwargs):
        self.matricula = kwargs.pop('matricula')
        super().__init__(*args, **kwargs)
        self.fields['turma_destino'].queryset = Turma.objects.exclude(pk=self.matricula.turma_id).order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')

        if status == StatusMatriculaTurma.RELOCADO:
            if not cleaned_data.get('turma_destino'):
                self.add_error('turma_destino', "Obrigatório para Relocado.")
        elif status == StatusMatriculaTurma.TRANSFERIDO:
            if not cleaned_data.get('motivo_saida'):
                self.add_error('motivo_saida', "Obrigatório para Transferido.")
            if not cleaned_data.get('data_fim'):
                self.add_error('data_fim', "Obrigatório.")
            if not cleaned_data.get('ata_encerramento'):
                self.add_error('ata_encerramento', "Obrigatório.")
        elif status in (StatusMatriculaTurma.REPROVADO, StatusMatriculaTurma.MATRICULA_EXCLUIDA):
            if not cleaned_data.get('data_fim'):
                self.add_error('data_fim', "Obrigatório.")
            if not cleaned_data.get('ata_encerramento'):
                self.add_error('ata_encerramento', "Obrigatório.")

        return cleaned_data


class RevisarAprovacaoForm(forms.Form):
    """
    1º clique de "Encerrar Turma" (docs/37, seção 8-A, fechada em 07/09/2026)
    — um campo BooleanField por aluno ainda CURSANDO, marcado por padrão
    (self.matriculas_cursando guarda a lista, na mesma ordem usada para criar
    os campos — usado pelo template via form.linhas para parear cada
    matrícula com seu checkbox correspondente).
    """

    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop('turma')
        super().__init__(*args, **kwargs)
        self.matriculas_cursando = list(
            MatriculaTurma.objects.filter(turma=self.turma, status=StatusMatriculaTurma.CURSANDO)
            .select_related('atribuicao_funcao__pessoa')
            .order_by('numero_na_turma')
        )
        for matricula in self.matriculas_cursando:
            self.fields[f'aprovar_{matricula.pk}'] = forms.BooleanField(
                required=False, initial=True, label=matricula.atribuicao_funcao.pessoa.nome_completo,
            )

    def linhas(self):
        for matricula in self.matriculas_cursando:
            yield matricula, self[f'aprovar_{matricula.pk}']

    def matriculas_aprovadas_ids(self):
        return [m.pk for m in self.matriculas_cursando if self.cleaned_data.get(f'aprovar_{m.pk}')]


class EncerrarTurmaForm(forms.Form):
    """
    2º clique de "Encerrar Turma" (docs/37, seção 4.4). 'ata_encerramento'
    fica escondida para Turma de Módulo Básico (nunca fecha vínculo) — para
    Especializado/Extracurricular, é exigida (mesmo que, no caso do
    Extracurricular, acabe não sendo usada para quem está acumulando com uma
    Turma regular — simplificação aceita por ora, ver docs/37 seção 7).
    """
    data_encerramento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label="Data de Encerramento"
    )
    ata_encerramento = forms.ModelChoiceField(
        queryset=Ata.objects.filter(finalidade=FinalidadeAta.TERMINO_VINCULO).order_by('-data'),
        required=False, label="Ata de Término de Vínculo",
    )

    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop('turma')
        super().__init__(*args, **kwargs)
        if self.turma.oferta_modulo.modulo.categoria == CategoriaModulo.BASICO:
            self.fields['ata_encerramento'].widget = forms.HiddenInput()
        else:
            self.fields['ata_encerramento'].required = True