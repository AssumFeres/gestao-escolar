"""
pessoas/services.py

Camada de Services: regras de negócio que envolvem mais de uma entidade,
ou que precisam de validação além do que o Model sozinho garante.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from infraestrutura.cep.adapters import ViaCepClient


class CadastrarPessoaComFuncaoService:
    """
    SRP: orquestra o cadastro de Pessoa + AtribuicaoFuncao + extensões específicas por
    categoria, numa transação única, buscando Pessoa existente pelo CPF antes de criar
    uma nova (evita duplicidade quando a mesma pessoa acumula uma nova Função ou repete
    curso).

    Para Docente, cadastra até a etapa preenchível por Secretaria/Aux. Administrativo
    (dados básicos + Formações). Requisitos de Contratação e Capacidades/Disciplinas
    (seções 6-7 da FE 008) ficam para PreencherRequisitosEDisciplinasDocenteService,
    chamado numa segunda tela — depende de as Formações já estarem salvas com id.

    Regra de negócio: uma Pessoa com Função de Discente (identificada pela existência de
    DadosDiscente associado a alguma AtribuicaoFuncao dela, nunca pelo texto de Funcao.nome
    — nome é editável, estrutura não) não pode acumular outra Função.

    PendenciaCadastro (documentação física pendente) é universal — não depende da
    categoria da Função, diferente de Formação/Experiência/Histórico de Vínculo Formal.
    """

    def executar(
        self,
        dados_pessoa: dict,
        funcao,
        dados_atribuicao: dict,
        dados_extensao: dict = None,
        formacoes: list = None,
        experiencias: list = None,
        historico_vinculo_formal: list = None,
        pendencias: list = None,
    ):
        from .models import (
            Pessoa, AtribuicaoFuncao, CategoriaFuncao,
            DadosDiscente, DadosDocente, FormacaoDocente,
            ExperienciaProfissional, HistoricoVinculoFormal, PendenciaCadastro,
        )

        with transaction.atomic():
            pessoa_ja_existe = Pessoa.objects.filter(cpf=dados_pessoa['cpf']).exists()

            if not pessoa_ja_existe:
                # Só vale checar duplicidade de RM/RA/CANAC quando uma Pessoa NOVA
                # será criada — se o CPF já existe, os valores de dados_pessoa são
                # só `defaults` (ignorados pelo get_or_create), não há inserção nova.
                campos_unicos = [
                    ('registro_matricula', 'RM'),
                    ('registro_aluno', 'RA'),
                    ('codigo_anac', 'CANAC'),
                ]
                for campo, rotulo in campos_unicos:
                    valor = dados_pessoa.get(campo)
                    if valor and Pessoa.objects.filter(**{campo: valor}).exists():
                        raise ValidationError(
                            f"{rotulo} '{valor}' já está em uso por outra pessoa."
                        )

            if funcao.categoria == CategoriaFuncao.DISCENTE:
                codigo_cma = (dados_extensao or {}).get('codigo_matricula_anac')
                if codigo_cma and DadosDiscente.objects.filter(codigo_matricula_anac=codigo_cma).exists():
                    raise ValidationError(
                        f"Código de Matrícula ANAC '{codigo_cma}' já está em uso."
                    )

            pessoa, criada = Pessoa.objects.get_or_create(
                cpf=dados_pessoa['cpf'],
                defaults=dados_pessoa,
            )

            if not criada:
                ja_e_discente = pessoa.atribuicoes.filter(dados_discente__isnull=False).exists()
                if ja_e_discente:
                    raise ValidationError(
                        "Esta pessoa já possui a Função Discente e não pode acumular outra Função."
                    )

            atribuicao = AtribuicaoFuncao.objects.create(
                pessoa=pessoa, funcao=funcao, **dados_atribuicao
            )

            dados_docente = None

            if funcao.categoria == CategoriaFuncao.DISCENTE:
                DadosDiscente.objects.create(atribuicao=atribuicao, **(dados_extensao or {}))

            elif funcao.categoria == CategoriaFuncao.DOCENTE:
                dados_docente = DadosDocente.objects.create(atribuicao=atribuicao, **(dados_extensao or {}))
                for formacao in (formacoes or []):
                    FormacaoDocente.objects.create(dados_docente=dados_docente, **formacao)

            elif funcao.categoria == CategoriaFuncao.GESTAO:
                for experiencia in (experiencias or []):
                    ExperienciaProfissional.objects.create(atribuicao=atribuicao, **experiencia)

            # Comum a Docente e Gestão, nunca Discente
            if funcao.categoria in (CategoriaFuncao.DOCENTE, CategoriaFuncao.GESTAO):
                for historico in (historico_vinculo_formal or []):
                    HistoricoVinculoFormal.objects.create(atribuicao=atribuicao, **historico)

            # Universal — qualquer categoria, sem condicional
            for pendencia in (pendencias or []):
                PendenciaCadastro.objects.create(atribuicao=atribuicao, **pendencia)

        return pessoa, atribuicao, dados_docente


class PreencherRequisitosEDisciplinasDocenteService:
    """
    SRP: completa o cadastro de um Docente já existente — Requisitos de Contratação
    (seção 6 da FE 008) e Disciplinas Habilitadas/Capacidade (seção 7) — etapa que só
    pode acontecer depois que as Formações (tabelas 3-5) já estão salvas, já que os
    Requisitos e a comprovação de Capacidade referenciam uma Formação existente.
    """

    def executar(self, dados_docente, dados_requisitos: dict, capacidades: list):
        from .models import Capacidade

        with transaction.atomic():
            dados_docente.experiencia_docente_comprovada = dados_requisitos.get('experiencia_docente_comprovada', '')
            dados_docente.formacao_especifica_comprobatoria = dados_requisitos.get('formacao_especifica_comprobatoria')
            dados_docente.save()

            for capacidade in (capacidades or []):
                Capacidade.objects.create(dados_docente=dados_docente, **capacidade)

        return dados_docente


class BuscarEnderecoPorCepService:
    """DIP: depende da abstração (porta), não da implementação concreta (ViaCEP)."""

    def __init__(self, cliente_cep=None):
        self.cliente_cep = cliente_cep or ViaCepClient()

    def executar(self, cep: str):
        return self.cliente_cep.buscar_endereco(cep)
