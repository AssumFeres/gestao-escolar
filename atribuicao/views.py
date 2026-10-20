from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Sum

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

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = RevisarAprovacaoForm(request.POST, turma=turma)
        if form.is_valid():
            PromoverAprovadosService().executar(turma, form.cleaned_data.get('aprovados_ids', []))
            if request.GET.get('parcial') == '1':
                return JsonResponse({'sucesso': True})
            return redirect('gerenciar-turma', pk=turma.pk)
        return render(request, self._template(request), {'form': form, 'turma': turma})


class EncerrarTurmaView(View):
    """2º clique de "Encerrar Turma" (docs/37, seção 4.4) — salva ata_encerramento, data_fim e muda Turma para ENCERRADA."""

    def _template(self, request):
        return 'atribuicao/_form_encerrar_turma_fragment.html' if request.GET.get('parcial') == '1' \
            else 'atribuicao/form_encerrar_turma.html'

    def get(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = EncerrarTurmaForm()
        return render(request, self._template(request), {'form': form, 'turma': turma})

    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk)
        form = EncerrarTurmaForm(request.POST)
        if form.is_valid():
            EncerrarTurmaService().executar(
                turma, form.cleaned_data['data_fim'], form.cleaned_data['ata_encerramento']
            )
            if request.GET.get('parcial') == '1':
                return JsonResponse({'sucesso': True})
            return redirect('gerenciar-turma', pk=turma.pk)
        return render(request, self._template(request), {'form': form, 'turma': turma})


# ======================================================================
# 📂 VIEWS DE SUPORTE ADICIONAIS EXIGIDAS PELO SEU ARQUIVO DE ROTAS
# ======================================================================

def horarios_view(request):
    """Lógica para processar e renderizar a definição da grade horária semanal."""
    if request.method == 'POST':
        atribuicao_id = request.POST.get('atribuicao')
        dia_semana = request.POST.get('dia_semana')
        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')

        try:
            atribuicao = Atribuicao.objects.get(pk=atribuicao_id)
            HorarioAula.objects.create(
                atribuicao=atribuicao,
                dia_semana=dia_semana,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim
            )
            messages.success(request, "Horário fixado na grade semanal com sucesso!")
            return redirect('horarios')
        except Exception as e:
            messages.error(request, f"Erro operacional ao salvar horário: {e}")
            return redirect('horarios')

    atribuigoes = Atribuicao.objects.all().select_related('disciplina', 'instrutor', 'turma').order_by('turma__nome', 'disciplina__nome')
    horarios = HorarioAula.objects.all().select_related('atribuicao__disciplina', 'atribuicao__turma').order_by('dia_semana', 'horario_inicio')
    dias_semana = [
        ('SEG', 'Segunda-feira'), ('TER', 'Terça-feira'), ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'), ('SEX', 'Sexta-feira'),
    ]
    return render(request, 'atribuicao/horarios.html', {'atribuigoes': atribuigoes, 'horarios': horarios, 'dias_semana': dias_semana})


def registro_instrucao_view(request):
    """Controlador para listagem histórica e gravação de diários de classe."""
    if request.method == 'POST':
        data_instrucao = request.POST.get('data_instrucao')
        carga_horaria = request.POST.get('carga_horaria')
        tipo = request.POST.get('tipo')
        conteudo = request.POST.get('conteudo')

        if request.user.is_authenticated:
            RegistroInstrucao.objects.create(
                instrutor=request.user,
                data_instrucao=data_instrucao,
                carga_horaria=carga_horaria,
                tipo=tipo,
                conteudo=conteudo
            )
            return redirect('registro_instrucao')

    # Alimenta o {% for registro in registros %} do seu HTML
    registros = RegistroInstrucao.objects.all().order_by('-data_instrucao')
    return render(request, 'atribuicao/registro_instrucao.html', {'registros': registros})


def relatorios_view(request):
    """Centralizador analítico de dados gerenciais do app de atribuição."""
    context = {
        'total_horas_ministradas': RegistroInstrucao.objects.aggregate(total=Sum('carga_horaria'))['total'] or 0,
        'total_matriculas_ativas': MatriculaTurma.objects.filter(status=StatusMatriculaTurma.CURSANDO).count(),
        'total_atribuigoes': Atribuicao.objects.count(),
    }
    return render(request, 'atribuicao/relatorios.html', context)


def atribuicao_view(request):
    """Redirecionamento automático da rota raiz para a listagem padrão de turmas."""
    return redirect('lista-turmas')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cadastros.models import Pessoa, Turma  

@login_required
def dashboard_gestao_view(request):
    # 1. Contagem dinâmica de Alunos e Turmas
    total_alunos = Pessoa.objects.exclude(registro_aluno__isnull=True).exclude(registro_aluno='').count()
    total_turmas = Turma.objects.count()  
    
    # 2. Cálculo automático de inconsistências
    alunos_sem_cpf = Pessoa.objects.exclude(registro_aluno__isnull=True).exclude(registro_aluno='').filter(cpf='').count()
    pessoas_sem_rm = Pessoa.objects.filter(registro_matricula__isnull=True).count()
    
    total_alertas = alunos_sem_cpf + pessoas_sem_rm
    
    context = {
        'total_alunos_ativos': total_alunos,  
        'turmas_andamento': total_turmas,     
        'alertas_pendentes': total_alertas,  
    }
    return render(request, 'atribuicao/dashboard.html', context)


@login_required
def contratos_gestao_view(request):
    """
    Função oficial mapeada no urls.py para gerenciar os contratos da EMCA.
    """
    # 1. Captura os parâmetros de busca do formulário HTML
    pesquisa = request.GET.get('pesquisa', '').strip()
    status_filtro = request.GET.get('status', '').strip()

    # 2. Busca os contratos no banco de dados trazendo o relacionamento do instrutor de forma otimizada
    contratos = ContratoFinanceiro.objects.all().select_related('instrutor')

    # 3. Regras de Filtragem baseadas no que o usuário digita na tela
    if pesquisa:
        from django.db.models import Q
        contratos = contratos.filter(
            Q(numero_contrato__icontains=pesquisa) | 
            Q(numero_processo__icontains=pesquisa) |
            Q(instrutor__first_name__icontains=pesquisa) |
            Q(instrutor__last_name__icontains=pesquisa) |
            Q(credor_razao_social__icontains=pesquisa)
        )

    if status_filtro:
        contratos = contratos.filter(status=status_filtro)

    # 4. Cálculo dos indicadores reais para alimentar os cards do topo
    total_vigentes = contratos.filter(status='VIGENTE').count()
    total_empenhado = contratos.aggregate(total=Sum('valor_total_empenhado'))['total'] or 0.00

    # 5. Organiza o contexto com todas as variáveis que o HTML precisa ler
    context = {
        'contratos': contratos,
        'total_vigentes': total_vigentes,
        'total_empenhado': total_empenhado,
    }
    
    return render(request, 'atribuicao/contratos.html', context)

from django.shortcuts import render
from .models import ContratoFinanceiro

def contratos_financeiros_view(request):
    # Traz os contratos do banco ordenados pela vigência
    contratos = ContratoFinanceiro.objects.all().select_related('instrutor')
    
    context = {
        'contratos': contratos,
    }
    return render(request, 'atribuicao/contratos.html', context)

from django.db.models import Q, Sum  

class ContratosFinanceirosView(View):
    """
    Controlador para a tela de Gestão de Contratos da EMCA.
    Lista as informações com filtros dinâmicos e soma de empenhos.
    """
    def get(self, request):
        # 1. Pega os termos de busca passados pelo formulário HTML
        pesquisa = request.GET.get('pesquisa', '').strip()
        status_filtro = request.GET.get('status', '').strip()

        # Importando aqui dentro para evitar qualquer erro de importação circular no topo
        from .models import ContratoFinanceiro  

        # 2. Inicia a consulta relacionando o Usuário/Instrutor de forma otimizada
        contratos = ContratoFinanceiro.objects.all().select_related('instrutor')

        # 3. Regras de Filtragem
        if pesquisa:
            contratos = contratos.filter(
                Q(numero_contrato__icontains=pesquisa) | 
                Q(numero_processo__icontains=pesquisa) |
                Q(instrutor__first_name__icontains=pesquisa) |
                Q(instrutor__last_name__icontains=pesquisa) |
                Q(credor_razao_social__icontains=pesquisa)
            )

        if status_filtro:
            contratos = contratos.filter(status=status_filtro)

        # 4. Cálculo dos Indicadores para os cards do painel
        total_vigentes = contratos.filter(status='VIGENTE').count()
        total_empenhado = contratos.aggregate(total=Sum('valor_total_empenhado'))['total'] or 0.00

        # 5. Montagem do contexto que será lido pelas tags do template
        context = {
            'contratos': contratos,
            'total_vigentes': total_vigentes,
            'total_empenhado': total_empenhado,
        }
        
        return render(request, 'atribuicao/contratos.html', context)
