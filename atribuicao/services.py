"""
atribuicao/services.py

Nunca escreve direto em campos de Models de `cadastros` sem passar por um
Service exposto lá (IniciarTurmaService, EncerrarVinculoService,
ObterOuCriarAtribuicaoDiscenteService) — ver docs/37, seção 1.
"""

from django.db import transaction

from django.db.models import Max
from django.utils import timezone

from cadastros.services import IniciarTurmaService, EncerrarVinculoService
from .models import MatriculaTurma, StatusMatriculaTurma


def atribuicoes_elegiveis_para_turma_regular():
    """
    Discentes ATIVOS "Aguardando Atribuição" (nunca tiveram MatriculaTurma)
    ou "Aguardando Turma" (última MatriculaTurma é RELOCADO, ou é APROVADO
    num Módulo categoria=BASICO) — docs/37, seção 6. Não usado para Turma
    Extracurricular, que aceita qualquer Pessoa (docs/37, seção 7).
    """
    from cadastros.models import AtribuicaoFuncao, SituacaoAtribuicao, CategoriaModulo

    elegiveis_ids = []
    ativos = AtribuicaoFuncao.objects.filter(
        dados_discente__isnull=False, situacao=SituacaoAtribuicao.ATIVO
    )
    for atrib in ativos:
        ultima = atrib.matriculas_turma.select_related('turma__oferta_modulo__modulo').order_by('-id').first()
        if ultima is None:
            elegiveis_ids.append(atrib.id)
        elif ultima.status == StatusMatriculaTurma.RELOCADO:
            elegiveis_ids.append(atrib.id)
        elif ultima.status == StatusMatriculaTurma.APROVADO and ultima.turma.oferta_modulo.modulo.categoria == CategoriaModulo.BASICO:
            elegiveis_ids.append(atrib.id)

    return AtribuicaoFuncao.objects.filter(id__in=elegiveis_ids)


class FinalizarPlanejamentoService:
    """
    Botão "Finalizar Planejamento" (docs/37, seção 4.2). Em massa, para cada
    MatriculaTurma da Turma: atribui numero_na_turma (ordem alfabética pelo
    nome da Pessoa — nunca muda depois), grava data_inicio/ata_inicio. Depois,
    chama IniciarTurmaService (cadastros) para avançar Turma.situacao.
    """

    def executar(self, turma, data_inicio, ata_inicio):
        with transaction.atomic():
            matriculas = list(
                MatriculaTurma.objects.filter(turma=turma)
                .select_related('atribuicao_funcao__pessoa')
                .order_by('atribuicao_funcao__pessoa__nome_completo')
            )
            for indice, matricula in enumerate(matriculas, start=1):
                matricula.numero_na_turma = indice
                matricula.data_inicio = data_inicio
                matricula.ata_inicio = ata_inicio
                matricula.save()

            IniciarTurmaService().executar(turma)

        return turma


class AlterarStatusMatriculaService:
    """
    Botão "Editar/CRU" enquanto a Turma está EM_ANDAMENTO (docs/37, seção 4.3).
    Só chamado quando matricula.status ainda é CURSANDO (imposto pela View).

    RELOCADO: fecha esta linha (data_fim=hoje) e CRIA uma MatriculaTurma nova
    na Turma destino (CURSANDO, numero_na_turma=MAX+1 de lá). NÃO mexe em
    AtribuicaoFuncao — o vínculo institucional continua ATIVO, sem Ata.

    REPROVADO/TRANSFERIDO/MATRICULA_EXCLUIDA: sempre fim de ciclo na EMCA,
    independente do Módulo (docs/37, seção 8-B, fechada em 07/09/2026) —
    atualiza esta mesma linha (data_fim + ata_encerramento) e chama
    EncerrarVinculoService (cadastros) sobre a AtribuicaoFuncao.
    """

    def executar(self, matricula, status, *, turma_destino=None, motivo_saida='',
                 data_fim=None, ata_encerramento=None):
        with transaction.atomic():
            if status == StatusMatriculaTurma.RELOCADO:
                hoje = timezone.now().date()
                matricula.status = StatusMatriculaTurma.RELOCADO
                matricula.data_fim = hoje
                matricula.save()

                proximo_numero = (
                    MatriculaTurma.objects.filter(turma=turma_destino)
                    .aggregate(Max('numero_na_turma'))['numero_na_turma__max'] or 0
                ) + 1
                MatriculaTurma.objects.create(
                    atribuicao_funcao=matricula.atribuicao_funcao,
                    turma=turma_destino,
                    status=StatusMatriculaTurma.CURSANDO,
                    numero_na_turma=proximo_numero,
                    data_inicio=hoje,
                )
            else:
                matricula.status = status
                matricula.motivo_saida = motivo_saida
                matricula.data_fim = data_fim
                matricula.ata_encerramento = ata_encerramento
                matricula.save()
                EncerrarVinculoService().executar(matricula.atribuicao_funcao, data_fim)

        return matricula