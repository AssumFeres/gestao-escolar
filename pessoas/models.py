"""
pessoas/models.py

Módulo de domínio: Gestão de Pessoas.

Classes:
    Pessoa                — dados cadastrais da pessoa física, com Endereco como VO embutido;
                            inclui identificação ampliada (FE 007/FE 008) e identificadores
                            específicos (RM, RA, CANAC).
    Disciplina             — versão mínima; campo 'modulo' será adicionado no módulo de Turmas.
    CategoriaFuncao        — enum que classifica uma Funcao como Discente/Docente/Gestão,
                            usado pela interface para decidir qual formulário exibir
                            (não é regra de negócio — essa mora nas extensões, por estrutura).
    Funcao                 — catálogo aberto de cargos/funções (Diretor, Coordenador de
                            Curso de X, Docente, Discente, etc.); id + nome livre + categoria.
    AtribuicaoFuncao       — liga Pessoa a Funcao; dados comuns a qualquer atribuição
                            (situação, datas, ativo). Substitui o antigo Vinculo.
    DadosDiscente          — extensão de AtribuicaoFuncao (OneToOne) para Discente:
                            matrícula ANAC, documentação de estrangeiro, contato de
                            emergência, responsável legal.
    DadosDocente           — extensão de AtribuicaoFuncao (OneToOne) para Docente.
    Capacidade             — aptidão de um DadosDocente para ministrar uma Disciplina.
    ExperienciaProfissional — histórico profissional ligado a uma AtribuicaoFuncao,
                            relevante apenas para Funções de categoria Gestão (FOP 402).

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
    # Identificadores específicos (comuns a qualquer categoria)
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    registro_aluno = models.CharField(max_length=20, unique=True, blank=True, verbose_name="RA")
    registro_matricula = models.CharField(max_length=20, unique=True, blank=True, verbose_name="RM")
    codigo_anac = models.CharField(max_length=20, unique=True, blank=True, verbose_name="CANAC")

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


class CategoriaFuncao(models.TextChoices):
    """
    Classifica uma Funcao para fins de interface (qual formulário/extensão exibir).
    NÃO é usado para regra de negócio — isso continua sendo decidido pela existência
    estrutural de DadosDiscente/DadosDocente, nunca por este campo nem pelo nome da Funcao.
    """
    DISCENTE = 'DISCENTE', 'Discente'
    DOCENTE = 'DOCENTE', 'Docente'
    GESTAO = 'GESTAO', 'Gestão'


class Funcao(models.Model):
    """Catálogo aberto: id + nome livre + categoria (para a interface saber qual formulário exibir)."""
    nome = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=10, choices=CategoriaFuncao.choices)

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


class DadosDiscente(models.Model):
    atribuicao = models.OneToOneField(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='dados_discente')

    codigo_matricula_anac = models.CharField(max_length=20, blank=True, verbose_name="Código de Matrícula ANAC")

    # Documentação de estrangeiro (FE 007)
    passaporte = models.CharField(max_length=20, blank=True)
    autorizacao_permanencia = models.CharField(max_length=50, blank=True)

    # Contato de emergência ("quem avisar") — texto simples, sem entidade própria
    contato_emergencia_nome = models.CharField(max_length=200, blank=True)
    contato_emergencia_parentesco = models.CharField(max_length=50, blank=True)
    contato_emergencia_telefone = models.CharField(max_length=20, blank=True)
    contato_emergencia_endereco = models.CharField(max_length=300, blank=True)

    # Responsável legal (só se menor de idade) — texto simples, reaproveitado nas assinaturas do FE 007
    responsavel_nome = models.CharField(max_length=200, blank=True)
    responsavel_endereco = models.CharField(max_length=300, blank=True)
    responsavel_identidade = models.CharField(max_length=20, blank=True)
    responsavel_orgao_expedidor = models.CharField(max_length=20, blank=True)
    responsavel_data_emissao = models.DateField(null=True, blank=True)
    responsavel_qualificacao = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.atribuicao.pessoa.nome_completo} - Dados Discente"


class DadosDocente(models.Model):
    atribuicao = models.OneToOneField(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='dados_docente')

    def __str__(self):
        return f"{self.atribuicao.pessoa.nome_completo} - Dados Docente"

    def possui_treinamento_valido(self) -> bool:
        return True


class Capacidade(models.Model):
    dados_docente = models.ForeignKey(DadosDocente, on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['dados_docente', 'disciplina'],
                condition=models.Q(ativo=True),
                name='unique_capacidade_ativa'
            )
        ]


class ExperienciaProfissional(models.Model):
    atribuicao = models.ForeignKey(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='experiencias_profissionais')
    organizacao = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cargo} em {self.organizacao}"