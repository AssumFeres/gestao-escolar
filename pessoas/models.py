"""
pessoas/models.py

Módulo de domínio: Gestão de Pessoas.

Classes:
    Pessoa                    — dados cadastrais da pessoa física, com Endereco como VO embutido.
    Vinculo                   — classe base para os tipos de vínculo com a instituição.
    VinculoDiscente            — vínculo de aluno; possui numero_matricula.
    VinculoDocente             — vínculo de instrutor; possui Capacidade e Treinamento.
    VinculoGestao              — vínculo de função administrativa; possui FuncaoGestao.
    FuncaoGestao               — cargo de gestão (Diretor, GQ, Coordenador, Secretaria).
    Habilitacao                — habilitação técnica, associável apenas a Coordenador.
    FuncaoGestaoHabilitacao     — tabela associativa entre FuncaoGestao e Habilitacao.
    Disciplina                 — versão mínima; campo 'modulo' será adicionado no módulo de Turmas.
    Capacidade                 — aptidão de um VinculoDocente para ministrar uma Disciplina.

Regras de negócio complexas ficam em services.py, não aqui.
"""

from dataclasses import dataclass

from django.db import models

from django.core.validators import RegexValidator


@dataclass(frozen=True)
class Endereco:
    """Value Object — imutável, sem identidade própria, existe só em função de uma Pessoa."""
    cep: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    uf: str

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro}, {self.cidade}/{self.uf}"


class Pessoa(models.Model):
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    # Identificação ampliada (FE 007 / FE 008)
    sexo = models.CharField(max_length=1, blank=True)
    identidade = models.CharField(max_length=20, blank=True)
    data_emissao_identidade = models.DateField(null=True, blank=True)
    orgao_expedidor_identidade = models.CharField(max_length=20, blank=True)
    naturalidade = models.CharField(max_length=100, blank=True)
    uf_naturalidade = models.CharField(max_length=2, blank=True)
    nacionalidade = models.CharField(max_length=100, blank=True)
    filiacao_1 = models.CharField(max_length=200, blank=True)
    filiacao_2 = models.CharField(max_length=200, blank=True)
    nivel_instrucao = models.CharField(max_length=100, blank=True)
    estado_civil = models.CharField(max_length=30, blank=True)
    raca_cor = models.CharField(max_length=30, blank=True)

    endereco_cep = models.CharField(max_length=8)
    endereco_logradouro = models.CharField(max_length=200)
    endereco_numero = models.CharField(max_length=10)
    endereco_complemento = models.CharField(max_length=100, blank=True)
    endereco_bairro = models.CharField(max_length=100)
    endereco_cidade = models.CharField(max_length=100)
    endereco_uf = models.CharField(max_length=2)

    ativo = models.BooleanField(default=True)

    @property
    def endereco(self) -> Endereco:
        return Endereco(
            cep=self.endereco_cep, logradouro=self.endereco_logradouro,
            numero=self.endereco_numero, complemento=self.endereco_complemento,
            bairro=self.endereco_bairro, cidade=self.endereco_cidade, uf=self.endereco_uf,
        )

    def atualizar_endereco(self, endereco: Endereco) -> None:
        self.endereco_cep = endereco.cep
        self.endereco_logradouro = endereco.logradouro
        self.endereco_numero = endereco.numero
        self.endereco_complemento = endereco.complemento
        self.endereco_bairro = endereco.bairro
        self.endereco_cidade = endereco.cidade
        self.endereco_uf = endereco.uf

    def __str__(self):
        return self.nome_completo


class Vinculo(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='vinculos')
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    @property
    def tipo_legivel(self):
        if hasattr(self, 'vinculodiscente'):
            return f"Discente (matricula {self.vinculodiscente.numero_matricula})"
        if hasattr(self, 'vinculodocente'):
            return "Docente"
        if hasattr(self, 'vinculogestao'):
            return "Gestao"
        return "Desconhecido"


class VinculoDiscente(Vinculo):
    numero_matricula = models.CharField(max_length=20, unique=True)
    situacao = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.pessoa.nome_completo} - Discente ({self.numero_matricula})"


class VinculoDocente(Vinculo):
    situacao = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.pessoa.nome_completo} - Docente"

    def possui_treinamento_valido(self) -> bool:
        return True


class VinculoGestao(Vinculo):
    situacao = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.pessoa.nome_completo} - Gestão"


class TipoFuncaoGestao(models.TextChoices):
    DIRETOR = 'DIRETOR', 'Diretor'
    GERENTE_DA_QUALIDADE = 'GERENTE_DA_QUALIDADE', 'Gerente da Qualidade'
    COORDENADOR = 'COORDENADOR', 'Coordenador'
    SECRETARIA = 'SECRETARIA', 'Secretaria'


class FuncaoGestao(models.Model):
    vinculo_gestao = models.ForeignKey(VinculoGestao, on_delete=models.CASCADE, related_name='funcoes')
    tipo_funcao = models.CharField(max_length=30, choices=TipoFuncaoGestao.choices)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vinculo_gestao.pessoa.nome_completo} - {self.get_tipo_funcao_display()}"


class Habilitacao(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class FuncaoGestaoHabilitacao(models.Model):
    """Só deve ter linhas quando FuncaoGestao.tipo_funcao == COORDENADOR (regra aplicada no Service)."""
    funcao_gestao = models.ForeignKey(FuncaoGestao, on_delete=models.CASCADE, related_name='habilitacoes')
    habilitacao = models.ForeignKey(Habilitacao, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.funcao_gestao} - {self.habilitacao}"


class Disciplina(models.Model):
    """Versão mínima — campo 'modulo' será adicionado quando o módulo de Turmas for construído."""
    sigla = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}$',
                message="Sigla deve conter exatamente 3 letras maiúsculas (ex: CBA, PSO, TCX)."
            )
        ]
    )
    nome = models.CharField(max_length=100, unique=True)
    carga_horaria = models.IntegerField()

    def __str__(self):
        return f"{self.sigla} - {self.nome}"
    


class Capacidade(models.Model):
    vinculo_docente = models.ForeignKey(VinculoDocente, on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['vinculo_docente', 'disciplina'],
                condition=models.Q(ativo=True),
                name='unique_capacidade_ativa'
            )
        ]


class Funcao(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class AtribuicaoFuncao(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='atribuicoes')
    funcao = models.ForeignKey(Funcao, on_delete=models.PROTECT, related_name='atribuicoes')
    situacao = models.CharField(max_length=30)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.funcao.nome}"