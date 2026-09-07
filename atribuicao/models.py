"""
atribuicao/models.py

Módulo Atribuição — identifica eventos (matrícula em turma, relocação,
reprovação, encerramento) mas nunca escreve direto nos Models de `cadastros`
(Pessoa/AtribuicaoFuncao/Ata/Turma/Modulo). A comunicação com `cadastros`
acontece por Services expostos lá (EncerrarVinculoService,
ObterOuCriarAtribuicaoDiscenteService) — ver docs/37, seção 1.

MatriculaTurma controla exclusivamente a relação Discente↔Turma — não
duplica nem substitui AtribuicaoFuncao. Ver docs/37, seção 3.
"""

from django.db import models


class StatusMatriculaTurma(models.TextChoices):
    CURSANDO = 'CURSANDO', 'Cursando'
    APROVADO = 'APROVADO', 'Aprovado'
    RELOCADO = 'RELOCADO', 'Relocado'
    TRANSFERIDO = 'TRANSFERIDO', 'Transferido'
    REPROVADO = 'REPROVADO', 'Reprovado'
    MATRICULA_EXCLUIDA = 'MATRICULA_EXCLUIDA', 'Matrícula Excluída'


class MotivoSaida(models.TextChoices):
    """Só preenchido quando status=TRANSFERIDO. MATRICULA_EXCLUIDA já é abandono por definição, sem campo extra (docs/37)."""
    ABANDONOU = 'ABANDONOU', 'Desistente - Abandonou'
    SOLICITOU = 'SOLICITOU', 'Desistente - Solicitou'


class MatriculaTurma(models.Model):
    """
    Regras de negócio completas em docs/37. Resumo:
    - Delete físico só permitido enquanto Turma.situacao == PLANEJADA.
    - 'numero_na_turma' nunca muda depois de atribuído (referência formal
      usada por professor/secretaria) — atribuído em massa (ordem alfabética)
      no "Finalizar Planejamento", ou MAX+1 para quem entra depois.
    - Relocação: fecha esta linha (RELOCADO + data_fim) e CRIA uma nova
      MatriculaTurma na turma destino (CURSANDO) — nunca edita in-place.
    - Reprovado/Transferido/Matrícula Excluída: edita esta mesma linha
      (fim de linha na mesma turma, não é troca de turma).
    """
    atribuicao_funcao = models.ForeignKey(
        'cadastros.AtribuicaoFuncao', on_delete=models.PROTECT, related_name='matriculas_turma'
    )
    turma = models.ForeignKey('cadastros.Turma', on_delete=models.PROTECT, related_name='matriculas')

    numero_na_turma = models.PositiveSmallIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=StatusMatriculaTurma.choices, default=StatusMatriculaTurma.CURSANDO)
    motivo_saida = models.CharField(max_length=20, choices=MotivoSaida.choices, blank=True)

    # Vazios enquanto a Turma está PLANEJADA; preenchidos em massa (Finalizar
    # Planejamento) ou individualmente (relocação/saída no meio do ano).
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    ata_inicio = models.ForeignKey(
        'cadastros.Ata', on_delete=models.PROTECT, null=True, blank=True, related_name='+'
    )
    ata_encerramento = models.ForeignKey(
        'cadastros.Ata', on_delete=models.PROTECT, null=True, blank=True, related_name='+'
    )

    observacao = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['atribuicao_funcao', 'turma'], name='unique_atribuicao_por_turma'),
            models.UniqueConstraint(fields=['turma', 'numero_na_turma'], name='unique_numero_por_turma'),
        ]

    def __str__(self):
        return f"{self.atribuicao_funcao.pessoa.nome_completo} - {self.turma} ({self.get_status_display()})"
