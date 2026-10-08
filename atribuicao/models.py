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

    # Marca a linha criada como destino de uma Relocação (AlterarStatusMatriculaService)
    # — usado só para rotular o evento certo no Sumário Histórico de Vínculos
    # ("Relocação - entrada" vs. "Início na turma"), sem depender de adivinhar
    # por coincidência de data (frágil). Adicionado em 08/09/2026.
    criada_por_relocacao = models.BooleanField(default=False)

    observacao = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['atribuicao_funcao', 'turma'], name='unique_atribuicao_por_turma'),
            models.UniqueConstraint(fields=['turma', 'numero_na_turma'], name='unique_numero_por_turma'),
        ]

    def __str__(self):
        return f"{self.atribuicao_funcao.pessoa.nome_completo} - {self.turma} ({self.get_status_display()})"

from django.db import models
from django.contrib.auth.models import User # Ou o model de Instrutor se seu amigo já tiver criado

class RegistroInstrucao(models.Model):
    TIPO_CHOICES = [
        ('TEORICA', 'Teórica'),
        ('PRATICA', 'Prática'),
        ('AVALIACAO', 'Avaliação/Exame'),
    ]

    # Relacionamentos (Chaves Estrangeiras)
    instrutor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Instrutor")
    # Se já existir um model de Turma, descomente a linha abaixo:
    # turma = models.ForeignKey(Turma, on_delete=models.PROTECT, verbose_name="Turma")

    # Dados da Instrução
    data_instrucao = models.DateField(verbose_name="Data da Instrução")
    carga_horaria = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Carga Horária (Horas)")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='TEORICA', verbose_name="Tipo de Instrução")
    
    # Textos detalhados
    conteudo = models.TextField(verbose_name="Conteúdo Programático Ministrado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações/Ocorrências")

    # Controle do Sistema
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de Instrução"
        verbose_name_plural = "Registros de Instrução"
        ordering = ['-data_instrucao']

    def __str__(self):
        return f"Instrução de {self.instrutor} em {self.data_instrucao}"
from django.db import models
from django.contrib.auth.models import User # Ou seu modelo de Instrutor personalizado

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Turma(models.Model):
    nome = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nome

# 1. MODELO DE ATRIBUIÇÃO
class Atribuicao(models.Model):
    instrutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='atribuigoes')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    ano_letivo = models.IntegerField(default=2026)

    class Meta:
        verbose_name_plural = "Atribuições"
        unique_together = ('instrutor', 'disciplina', 'turma', 'ano_letivo')

    def __str__(self):
        return f"{self.instrutor.username} - {self.disciplina.nome} ({self.turma.nome})"

# 2. MODELO DE HORÁRIOS
class HorarioAula(models.Model):
    DIAS_SEMANA = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
    ]
    atribuicao = models.ForeignKey(Atribuicao, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DIAS_SEMANA)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.dia_semana} | {self.horario_inicio} - {self.atribuicao.disciplina.nome}"

# 3. MODELO DE REGISTRO DE INSTRUÇÃO 

class RegistroInstrucao(models.Model):
    TIPO_CHOICES = [('Teórica', 'Teórica'), ('Prática', 'Prática')]
    
    # Adicionado null=True e blank=True para não travar o banco com dados antigos
    instrutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instrucoes_registradas', null=True, blank=True)
    atribuicao = models.ForeignKey(Atribuicao, on_delete=models.CASCADE, null=True, blank=True)
    
    data_instrucao = models.DateField()
    carga_horaria = models.DecimalField(max_digits=4, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    conteudo_programatico = models.TextField()

    class Meta:
        verbose_name = "Registro de Instrução"
        verbose_name_plural = "Registros de Instrução"

    def __str__(self):
        return f"{self.data_instrucao} - {self.instrutor.username if self.instrutor else 'Sem Instrutor'}"
