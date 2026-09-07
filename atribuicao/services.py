"""
atribuicao/services.py

Nunca escreve direto em campos de Models de `cadastros` sem passar por um
Service exposto lá (IniciarTurmaService, EncerrarVinculoService,
ObterOuCriarAtribuicaoDiscenteService) — ver docs/37, seção 1.
"""

from django.db import transaction

from cadastros.services import IniciarTurmaService
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
