"""
pessoas/models.py

Módulo de domínio: Gestão de Pessoas.

Classes:
    Pessoa                  — dados cadastrais da pessoa física, com Endereco como VO embutido;
                              inclui identificação ampliada (FE 007/FE 008) e identificadores
                              específicos (RM, RA, CANAC — opcionais, null=True para não
                              conflitar entre si na constraint unique quando vazios).
    Disciplina               — versão mínima; campo 'modulo' será adicionado no módulo de Turmas.
    CategoriaFuncao          — enum que classifica uma Funcao como Discente/Docente/Gestão,
                              usado pela interface para decidir qual formulário exibir
                              (não é regra de negócio — essa mora nas extensões, por estrutura).
    Funcao                   — catálogo aberto de cargos/funções (Diretor, Coordenador de
                              Curso de X, Docente, Discente, etc.); id + nome livre + categoria.
    VinculoFormal            — catálogo aberto de entidades de vínculo formal/contratual
                              (ex: FAPETI, PMT) — evita erro de digitação num dado repetido.
    AtribuicaoFuncao         — liga Pessoa a Funcao; dados comuns a qualquer atribuição
                              (situação, datas, ativo). Substitui o antigo Vinculo.
    HistoricoVinculoFormal   — histórico de VinculoFormal ao longo de uma AtribuicaoFuncao;
                              repetível (a entidade contratante pode mudar com o tempo).
                              Aplica-se só a categorias Docente e Gestão, nunca Discente.
    TipoPendencia            — enum dos tipos comuns de pendência documental no cadastro.
    PendenciaCadastro        — pendências de documentação física (certidão, RG, comprovante
                              de endereço, etc.), ligada a uma AtribuicaoFuncao. Universal:
                              aparece em Discente, Docente ou Gestão, sem restrição de
                              categoria — diferente de Formação/Experiência/Histórico, que
                              são condicionais. Usada para gerar o relatório operacional
                              de pendências por Turma/Aluno entregue ao Coordenador de Curso.
    DadosDiscente            — extensão de AtribuicaoFuncao (OneToOne) para Discente:
                              código de matrícula ANAC (específico do curso, diferente do
                              CANAC de Pessoa — ver nota no campo), documentação de
                              estrangeiro, contato de emergência, responsável legal.
    DadosDocente             — extensão de AtribuicaoFuncao (OneToOne) para Docente;
                              inclui os Requisitos de Contratação da FE 008 (RBAC 141).
    FormacaoDocente          — Graduação/Formação Profissional/Aperfeiçoamento (FE 008,
                              seções 3/4/5), tabela única com campo tipo_formacao (DRY).
                              Guarda atualizado_em para futura detecção de FE 008 desatualizada.
    Capacidade               — aptidão de um DadosDocente para ministrar uma Disciplina;
                              referencia o FormacaoDocente que comprova a capacidade.
                              Guarda atualizado_em pelo mesmo motivo de FormacaoDocente.
    ExperienciaProfissional  — histórico profissional ligado a uma AtribuicaoFuncao,
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
    # Identificadores específicos (comuns a qualquer categoria).
    # null=True além de blank=True: quando vazio, salva NULL (não string vazia) —
    # múltiplos NULL não conflitam na constraint unique=True, diferente de múltiplas
    # strings vazias, que o SQLite trata como duplicatas entre si (causava IntegrityError
    # ao cadastrar duas Pessoas sem preencher RM, por exemplo).
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    registro_matricula = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="RM"
    )
    registro_aluno = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="RA"
    )
    codigo_anac = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="CANAC",
        help_text="Identificador da pessoa perante a ANAC. Idealmente obrigatório, mas "
                   "pode ficar pendente no cadastro inicial (ver PendenciaCadastro)."
    )

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


class VinculoFormal(models.Model):
    """
    Catálogo aberto de entidades de vínculo formal/contratual (ex: FAPETI, PMT).
    Evita erro de digitação num dado que se repete e pode mudar com o tempo — mesmo
    raciocínio já aplicado a Funcao. Aplica-se só a Docente e Gestão, nunca a Discente.
    """
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


class HistoricoVinculoFormal(models.Model):
    """
    Histórico de VinculoFormal ao longo de uma AtribuicaoFuncao — repetível, porque a
    entidade contratante pode mudar com o tempo sem que a pessoa mude de Função na escola
    (ex: FAPETI de 2025 a 2026, depois FUSSUSS a partir de 2026, em aberto).
    """
    atribuicao = models.ForeignKey(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='historico_vinculo_formal')
    vinculo_formal = models.ForeignKey(VinculoFormal, on_delete=models.PROTECT, related_name='historicos')
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vinculo_formal.nome} ({self.data_inicio} - {self.data_fim or 'atual'})"


class TipoPendencia(models.TextChoices):
    """Tipos comuns de pendência documental — 'OUTRO' + descricao cobre casos incomuns."""
    CANAC = 'CANAC', 'CANAC'
    RM = 'RM', 'Registro de Matrícula'
    RA = 'RA', 'Registro de Aluno'
    CODIGO_MATRICULA_ANAC = 'CODIGO_MATRICULA_ANAC', 'Código de Matrícula ANAC'
    CERTIDAO_NASCIMENTO = 'CERTIDAO_NASCIMENTO', 'Certidão de Nascimento'
    CPF_FISICO = 'CPF_FISICO', 'CPF (documento físico)'
    RG = 'RG', 'RG/Carteira de Identidade'
    PASSAPORTE = 'PASSAPORTE', 'Passaporte + Autorização de Permanência (estrangeiro)'
    COMPROVANTE_ENDERECO = 'COMPROVANTE_ENDERECO', 'Comprovante de Endereço'
    CARTAO_VACINA = 'CARTAO_VACINA', 'Cartão de Vacina (menor de 18)'
    OUTRO = 'OUTRO', 'Outro'


class PendenciaCadastro(models.Model):
    """
    Pendências de documentação física do cadastro — universal, aparece em Discente,
    Docente ou Gestão (diferente de Formação/Experiência/Histórico, que são condicionais
    por categoria). Ligada a AtribuicaoFuncao, não a Pessoa, pensando no relatório
    operacional futuro (Turma -> Aluno -> Pendências) entregue ao Coordenador de Curso.
    """
    atribuicao = models.ForeignKey(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='pendencias')
    tipo = models.CharField(max_length=30, choices=TipoPendencia.choices)
    descricao = models.CharField(
        max_length=200, blank=True,
        help_text="Detalhe livre, usado sobretudo quando tipo=OUTRO."
    )
    resolvida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    resolvida_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.atribuicao.pessoa.nome_completo}"


class DadosDiscente(models.Model):
    atribuicao = models.OneToOneField(AtribuicaoFuncao, on_delete=models.CASCADE, related_name='dados_discente')

    # Diferente de Pessoa.codigo_anac (identifica a PESSOA perante a ANAC, permanente):
    # este é o código da MATRÍCULA específica (ex: 239.MCELT.25.00115 — Ciac.Habilitação.
    # Ano.Sequencial), muda a cada novo curso. Pode ficar pendente no cadastro inicial
    # (ver PendenciaCadastro, tipo CODIGO_MATRICULA_ANAC) até a ANAC processar.
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

    # Requisitos de Contratação (FE 008, seção 6, RBAC 141)
    experiencia_docente_comprovada = models.TextField(
        blank=True,
        help_text="Análise de declarações de serviço, CV, etc. — comprovação de experiência docente (RBAC 141)."
    )
    formacao_especifica_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        related_name='comprova_requisito_para',
        help_text="Curso que comprova formação específica na área de atuação (RBAC 141)."
    )

    def __str__(self):
        return f"{self.atribuicao.pessoa.nome_completo} - Dados Docente"

    def possui_treinamento_valido(self) -> bool:
        return True


class TipoFormacaoDocente(models.TextChoices):
    GRADUACAO = 'GRADUACAO', 'Graduação'
    FORMACAO_PROFISSIONAL = 'FORMACAO_PROFISSIONAL', 'Formação Profissional'
    APERFEICOAMENTO_PROFISSIONAL = 'APERFEICOAMENTO_PROFISSIONAL', 'Aperfeiçoamento Profissional'


class FormacaoDocente(models.Model):
    """
    Graduação/Formação Profissional/Aperfeiçoamento (FE 008, seções 3/4/5) — tabela única
    com campo tipo_formacao, evitando 3 Models quase idênticos (DRY).

    'atualizado_em' guarda quando este registro mudou pela última vez — não usado ainda,
    mas preparado para a futura funcionalidade de alertar quando a FE 008 impressa ficar
    desatualizada em relação ao banco (numeração "4.1" etc. é calculada, pode mudar com
    edições; ver item de Backlog "Alerta de FE 008 desatualizada").
    """
    dados_docente = models.ForeignKey(DadosDocente, on_delete=models.CASCADE, related_name='formacoes')
    tipo_formacao = models.CharField(max_length=30, choices=TipoFormacaoDocente.choices)
    curso = models.CharField(max_length=200)
    entidade = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    ano_conclusao = models.IntegerField()
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.curso} ({self.get_tipo_formacao_display()})"


class Capacidade(models.Model):
    """'atualizado_em': mesmo propósito de FormacaoDocente.atualizado_em, ver docstring acima."""
    dados_docente = models.ForeignKey(DadosDocente, on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    formacao_comprobatoria = models.ForeignKey(
        FormacaoDocente, on_delete=models.PROTECT, null=True, blank=True,
        help_text="Curso (FormacaoDocente) que comprova a capacidade de ministrar esta disciplina."
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

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
