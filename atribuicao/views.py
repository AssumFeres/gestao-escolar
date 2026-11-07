from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Sum, Count
from django.db import models
from django.views.generic import ListView, TemplateView

from cadastros.models import Turma, SituacaoTurma
from cadastros.views import ModalCrudMixin

from .forms import (
    AdicionarMatriculaTurmaForm, EditarMatriculaTurmaForm, FinalizarPlanejamentoForm,
    EditarStatusMatriculaForm, RevisarAprovacaoForm, EncerrarTurmaForm,
)
from .models import MatriculaTurma, StatusMatriculaTurma, RegistroInstrucao, HorarioAula, Atribuicao
from .services import (
    FinalizarPlanejamentoService, AlterarStatusMatriculaService,
    PromoverAprovadosService, EncerrarTurmaService,
)


class GerenciarTurmaView(DetailView):
    """
    Tela principal do módulo Atribuição — composição de alunos de uma Turma.
    Enquanto PLANEJADA: ordena por nome (numero_na_turma ainda não existe).
    Depois de Finalizar Planejamento: ordena por numero_na_turma (fixo).
    """
    model = Turma
    template_name = 'atribuicao/gerenciar_turma.html'
    context_object_name = 'turma'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matriculas = self.object.matriculas.select_related('atribuicao_funcao__pessoa')
        if self.object.situacao == SituacaoTurma.PLANEJADA:
            matriculas = matriculas.order_by('atribuicao_funcao__pessoa__nome_completo')
        else:
            matriculas = matriculas.order_by('numero_na_turma')
        context['matriculas'] = matriculas
        context['ha_cursando'] = self.object.matriculas.filter(status=StatusMatriculaTurma.CURSANDO).exists()
        return context


class AdicionarMatriculaTurmaView(ModalCrudMixin, CreateView):
    model = MatriculaTurma
    form_class = AdicionarMatriculaTurmaForm
    template_name = 'atribuicao/form_matricula.html'
    template_fragmento = 'atribuicao/_form_matricula_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.turma = get_object_or_404(Turma, pk=kwargs['pk'])
        if self.turma.situacao == SituacaoTurma.ENCERRADA:
            raise Http404("Não é possível adicionar aluno a uma Turma já Encerrada.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['turma'] = self.turma
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['turma'] = self.turma
        return context

    def get_success_url(self):
        return reverse('gerenciar-turma', kwargs={'pk': self.turma.pk})


class EditarMatriculaTurmaView(ModalCrudMixin, UpdateView):
    model = MatriculaTurma
    form_class = EditarMatriculaTurmaForm
    template_name = 'atribuicao/form_matricula.html'
    template_fragmento = 'atribuicao/_form_matricula_fragment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['turma'] = self.object.turma
        context['editando'] = True
        return context

    def get_success_url(self):
        return reverse('gerenciar-turma', kwargs={'pk': self.object.turma_id})


class ExcluirMatriculaTurmaView(ModalCrudMixin, DeleteView):
    """Delete físico — só permitido enquanto a Turma está PLANEJADA (docs/37, seção 3)."""
    model = MatriculaTurma
    template_name = 'cadastros/confirmar_exclusao.html'
    template_fragmento = 'cadastros/_confirmar_exclusao_fragment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.turma.situacao != SituacaoTurma.PLANEJADA:
            raise Http404("Só é possível excluir uma matrícula enquanto a Turma está Planejada.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_voltar'] = reverse('gerenciar-turma', kwargs={'pk': self.object.turma_id})
        return context

    def get_success_url(self):
        return reverse('gerenciar-turma', kwargs={'pk': self.object.turma_id})


class FinalizarPlanejamentoView(View):
    """
    Botão "Finalizar Planejamento" (docs/37, seção 4.2) — ação em lote, não
    um CRUD de instância única, por isso não usa ModalCrudMixin/CreateView;
    replica manualmente o mesmo contrato (fragmento no GET, JSON no POST com
    ?parcial=1) para funcionar com o modal-crud.js já existente.
    """

    def _template(self, request):
        return 'atribuicao/_form_finalizar_planejamento_fragment.html' if request.GET.get('parcial') == '1' \
            else 'atribuicao/form_finalizar_planejamento.html'

    def get(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = FinalizarPlanejamentoForm()
        return render(request, self._template(request), {'form': form, 'turma': turma})

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = FinalizarPlanejamentoForm(request.POST)
        if form.is_valid():
            FinalizarPlanejamentoService().executar(
                turma, form.cleaned_data['data_inicio'], form.cleaned_data['ata_inicio']
            )
            if request.GET.get('parcial') == '1':
                return JsonResponse({'sucesso': True})
            return redirect('gerenciar-turma', pk=turma.pk)
        return render(request, self._template(request), {'form': form, 'turma': turma})


class EditarStatusMatriculaView(View):
    """
    Botão "Editar/CRU" enquanto a Turma está EM_ANDAMENTO (docs/37, seção 4.3)
    — muda o status de CURSANDO para Relocado/Reprovado/Transferido/Matrícula
    Excluída. Não usa ModalCrudMixin/UpdateView (o Form não é um ModelForm —
    os campos variam por status escolhido, resolvidos via
    AlterarStatusMatriculaService, não um form.save() direto).
    """

    def _template(self, request):
        return 'atribuicao/_form_status_matricula_fragment.html' if request.GET.get('parcial') == '1' \
            else 'atribuicao/form_status_matricula.html'

    def _matricula_ou_404(self, pk):
        matricula = get_object_or_404(MatriculaTurma, pk=pk)
        if matricula.status != StatusMatriculaTurma.CURSANDO:
            raise Http404("Só é possível alterar o status de uma matrícula ainda Cursando.")
        return matricula

    def get(self, request, pk):
        matricula = self._matricula_ou_404(pk)
        form = EditarStatusMatriculaForm(matricula=matricula)
        return render(request, self._template(request), {'form': form, 'matricula': matricula})

    def post(self, request, pk):
        matricula = self._matricula_ou_404(pk)
        form = EditarStatusMatriculaForm(request.POST, matricula=matricula)
        if form.is_valid():
            AlterarStatusMatriculaService().executar(
                matricula, form.cleaned_data['status'],
                turma_destino=form.cleaned_data.get('turma_destino'),
                motivo_saida=form.cleaned_data.get('motivo_saida', ''),
                data_fim=form.cleaned_data.get('data_fim'),
                ata_encerramento=form.cleaned_data.get('ata_encerramento'),
            )
            if request.GET.get('parcial') == '1':
                return JsonResponse({'sucesso': True})
            return redirect('gerenciar-turma', pk=matricula.turma_id)
        return render(request, self._template(request), {'form': form, 'matricula': matricula})


class RevisarAprovacaoView(View):
    """1º clique de "Encerrar Turma" (docs/37, seção 4.4/8-A) — lista de revisão com checkbox por aluno Cursando."""

    def _template(self, request):
        return 'atribuicao/_form_revisar_aprovacao_fragment.html' if request.GET.get('parcial') == '1' \
            else 'atribuicao/form_revisar_aprovacao.html'

    def get(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = RevisarAprovacaoForm(turma=turma)
        return render(request, self._template(request), {'form': form, 'turma': turma})


class EncerrarTurmaView(View):
    """Ação de encerramento de turma."""

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = EncerrarTurmaForm(request.POST)
        if form.is_valid():
            EncerrarTurmaService().executar(turma, form.cleaned_data['ata_encerramento'])
            messages.success(request, f"Turma {turma.nome} encerrada com sucesso!")
        return redirect('gerenciar-turma', pk=turma.pk)


# ==========================================================
# SEÇÃO OPERACIONAL E PEDAGÓGICA (RECONSTRUÍDA)
# ==========================================================

def registro_instrucao_view(request):
    """Renderiza a tela operacional de registro de instrução."""
    instrucoes = RegistroInstrucao.objects.all().order_by('-data_instrucao')
    return render(request, 'atribuicao/registro_instrucao.html', {'instrucoes': instrucoes})


def horarios_view(request):
    """Renderiza os quadros de horários do módulo."""
    horarios = HorarioAula.objects.all()
    return render(request, 'atribuicao/horarios.html', {'horarios': horarios})


def relatorios_view(request):
    """Renderiza a central de relatórios operacionais."""
    return render(request, 'atribuicao/relatorios.html')


def atribuicao_view(request):
    """Renderiza a tela de listagem geral de atribuições."""
    atribuigoes = Atribuicao.objects.all()
    return render(request, 'atribuicao/atribuicao.html', {'atribuigoes': atribuigoes})


def dashboard_gestao_view(request):
    """Renderiza o painel operacional de gerenciamento de turmas."""
    return render(request, 'atribuicao/dashboard.html')

def contratos_gestao_view(request):
    """Renderiza a tela de contratos e prestação de serviços."""
    return render(request, 'atribuicao/contratos.html')


# ==========================================================
# MÓDULO DE QUALIDADE (DIRECIONADA AO NÚCLEO)
# ==========================================================

class TreinamentoListView(ListView):
    """Listagem de registros de instrução pedagógica."""

    model = RegistroInstrucao
    template_name = 'nucleo/treinamento.html'
    context_object_name = 'instrucoes'
    paginate_by = 15

    def get_queryset(self):
        return RegistroInstrucao.objects.select_related(
            'instrutor', 'atribuicao__disciplina', 'atribuicao__turma'
        ).order_by('-data_instrucao')


class AuditoriaInternaListView(ListView):
    """Histórico de movimentações de Atas oficiais."""

    model = MatriculaTurma
    template_name = 'nucleo/auditoria_interna.html'
    context_object_name = 'historico_vinculos'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        return MatriculaTurma.objects.filter(
            Q(ata_inicio__isnull=False) | Q(ata_encerramento__isnull=False)
        ).select_related('atribuicao_funcao__pessoa', 'turma', 'ata_inicio', 'ata_encerramento').order_by('-data_inicio')


class IndicadoresQualidadeView(TemplateView):
    """Painel analítico e consolidação de indicadores institucionais."""

    template_name = 'nucleo/indicadores_qualidade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = MatriculaTurma.objects.count()
        context['total_matriculas'] = total
        context['alunos_cursando'] = MatriculaTurma.objects.filter(status=StatusMatriculaTurma.CURSANDO).count()
        context['alunos_aprovados'] = MatriculaTurma.objects.filter(status=StatusMatriculaTurma.APROVADO).count()
        context['alunos_reprovados'] = MatriculaTurma.objects.filter(status=StatusMatriculaTurma.REPROVADO).count()
        
        evadidos = MatriculaTurma.objects.filter(
            status__in=[StatusMatriculaTurma.MATRICULA_EXCLUIDA, StatusMatriculaTurma.TRANSFERIDO]
        ).count()
        context['taxa_evasao'] = round((evadidos / total * 100), 1) if total > 0 else 0

        # Agregação de carga horária letiva
        horas = RegistroInstrucao.objects.aggregate(
            tot=Sum('carga_horaria'),
            teorica=Sum('carga_horaria', filter=models.Q(tipo='Teórica')),
            pratica=Sum('carga_horaria', filter=models.Q(tipo='Prática'))
        )
        context['horas_totais_instrucao'] = horas['tot'] or 0
        context['horas_teoricas'] = horas['teorica'] or 0
        context['horas_praticas'] = horas['pratica'] or 0

        total_h = context['horas_totais_instrucao']
        context['pct_teorica'] = round((context['horas_teoricas'] / total_h * 100), 1) if total_h > 0 else 0
        context['pct_pratica'] = round((context['horas_praticas'] / total_h * 100), 1) if total_h > 0 else 0

        # Gestão de contratos empenhados
        try:
            from .models import ContratoFinanceiro
            financeiro = ContratoFinanceiro.objects.aggregate(
                total_empenhado=Sum('valor_total_empenhado'),
                qtd_contratos=Count('id')
            )
            context['investimento_total'] = financeiro['total_empenhado'] or 0
            context['total_contratos'] = financeiro['qtd_contratos'] or 0
        except (ImportError, AttributeError):
            context['investimento_total'] = 0
            context['total_contratos'] = 0

        return context
