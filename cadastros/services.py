"""
cadastros/services.py

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

    Busca por CPF com reaproveitamento/edição de dados (decisão de 02/09/2026): quando
    a Pessoa já existe, os dados enviados em `dados_pessoa` deixam de ser ignorados
    (comportamento antigo do `get_or_create` puro) e passam a ATUALIZAR a Pessoa
    existente de verdade — exceto o CPF, que nunca muda. O fluxo esperado é a tela
    buscar a Pessoa pelo CPF primeiro e pré-preencher os campos com os dados atuais,
    para o usuário só editar o que precisa corrigir, nunca reenviar o formulário em
    branco por cima de um cadastro já preenchido.

    Regra de negócio — exclusividade da categoria Discente:

    - Pessoa com Discente ATIVO não pode acumular outra Função.
    - Pessoa com Docente ou Gestão ATIVO não pode receber uma Função Discente.
    - Docente e Gestão podem coexistir.
    - Atribuições INATIVAS não impedem uma nova atribuição.
    - Um ex-aluno pode retornar futuramente como Discente em uma nova
      AtribuicaoFuncao, desde que a anterior esteja encerrada.

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
            Pessoa,
            AtribuicaoFuncao,
            CategoriaFuncao,
            SituacaoAtribuicao,
            DadosDiscente,
            DadosDocente,
            FormacaoDocente,
            ExperienciaProfissional,
            HistoricoVinculoFormal,
            PendenciaCadastro,
        )

        with transaction.atomic():

            pessoa_existente = Pessoa.objects.filter(
                cpf=dados_pessoa['cpf']
            ).first()

            # ---------------------------------------------------------
            # DUPLICIDADE DE RM / RA / CANAC
            # ---------------------------------------------------------
            #
            # Exclui a própria Pessoa existente da verificação.
            # Isso evita que um valor que já pertence à própria pessoa
            # seja identificado incorretamente como duplicado.
            # ---------------------------------------------------------

            campos_unicos = [
                ('registro_matricula', 'RM'),
                ('registro_aluno', 'RA'),
                ('codigo_anac', 'CANAC'),
            ]

            for campo, rotulo in campos_unicos:

                valor = dados_pessoa.get(campo)

                if not valor:
                    continue

                consulta = Pessoa.objects.filter(
                    **{campo: valor}
                )

                if pessoa_existente:
                    consulta = consulta.exclude(
                        pk=pessoa_existente.pk
                    )

                if consulta.exists():
                    raise ValidationError(
                        f"{rotulo} '{valor}' já está em uso por outra pessoa."
                    )


            # ---------------------------------------------------------
            # DUPLICIDADE DO CÓDIGO DE MATRÍCULA ANAC
            # ---------------------------------------------------------

            if funcao.categoria == CategoriaFuncao.DISCENTE:

                codigo_cma = (
                    dados_extensao or {}
                ).get('codigo_matricula_anac')

                if (
                    codigo_cma
                    and DadosDiscente.objects.filter(
                        codigo_matricula_anac=codigo_cma
                    ).exists()
                ):
                    raise ValidationError(
                        f"Código de Matrícula ANAC "
                        f"'{codigo_cma}' já está em uso."
                    )


            # ---------------------------------------------------------
            # BUSCA OU CRIA A PESSOA
            # ---------------------------------------------------------

            pessoa, criada = Pessoa.objects.get_or_create(
                cpf=dados_pessoa['cpf'],
                defaults=dados_pessoa,
            )


            # ---------------------------------------------------------
            # PESSOA JÁ EXISTENTE
            # ---------------------------------------------------------

            if not criada:

                # Atualiza os dados cadastrais da Pessoa existente.
                # O CPF nunca é alterado.

                for campo, valor in dados_pessoa.items():

                    if campo != 'cpf':
                        setattr(
                            pessoa,
                            campo,
                            valor
                        )

                pessoa.save()


                # -----------------------------------------------------
                # REGRA DE EXCLUSIVIDADE DA CATEGORIA DISCENTE
                # -----------------------------------------------------
                #
                # Obtém todas as categorias das atribuições atualmente
                # ATIVAS da Pessoa.
                #
                # Exemplos possíveis:
                #
                # {'DOCENTE'}
                #
                # {'GESTAO'}
                #
                # {'DOCENTE', 'GESTAO'}
                #
                # {'DISCENTE'}
                #
                # Atribuições INATIVAS não entram nessa consulta.
                # -----------------------------------------------------

                categorias_ativas = set(
                    pessoa.atribuicoes
                    .filter(
                        situacao=SituacaoAtribuicao.ATIVO
                    )
                    .values_list(
                        'funcao__categoria',
                        flat=True
                    )
                )


                # -----------------------------------------------------
                # CASO 1
                #
                # A Pessoa já possui Discente ATIVO.
                #
                # Enquanto esse vínculo estiver ativo, nenhuma nova
                # Função poderá ser atribuída.
                # -----------------------------------------------------

                if CategoriaFuncao.DISCENTE in categorias_ativas:

                    raise ValidationError(
                        "Esta pessoa já possui a Função Discente ativa "
                        "e não pode acumular outra Função."
                    )


                # -----------------------------------------------------
                # CASO 2
                #
                # A nova Função é Discente.
                #
                # Se a Pessoa já possui qualquer outra categoria ativa
                # (Docente ou Gestão), a nova atribuição é bloqueada.
                #
                # Docente + Gestão continua permitido porque esta regra
                # somente é executada quando a NOVA função é Discente.
                # -----------------------------------------------------

                if (
                    funcao.categoria == CategoriaFuncao.DISCENTE
                    and categorias_ativas
                ):

                    raise ValidationError(
                        "Esta pessoa já possui uma Função ativa de "
                        "Docente ou Gestão e não pode ser cadastrada "
                        "como Discente enquanto esse vínculo estiver ativo."
                    )


            # ---------------------------------------------------------
            # CRIA A ATRIBUIÇÃO DA FUNÇÃO
            # ---------------------------------------------------------

            atribuicao = AtribuicaoFuncao.objects.create(
                pessoa=pessoa,
                funcao=funcao,
                **dados_atribuicao
            )


            dados_docente = None


            # ---------------------------------------------------------
            # EXTENSÃO DISCENTE
            # ---------------------------------------------------------

            if funcao.categoria == CategoriaFuncao.DISCENTE:

                DadosDiscente.objects.create(
                    atribuicao=atribuicao,
                    **(dados_extensao or {})
                )


            # ---------------------------------------------------------
            # EXTENSÃO DOCENTE
            # ---------------------------------------------------------

            elif funcao.categoria == CategoriaFuncao.DOCENTE:

                dados_docente = DadosDocente.objects.create(
                    atribuicao=atribuicao,
                    **(dados_extensao or {})
                )

                for formacao in (formacoes or []):

                    FormacaoDocente.objects.create(
                        dados_docente=dados_docente,
                        **formacao
                    )


            # ---------------------------------------------------------
            # EXTENSÃO GESTÃO
            # ---------------------------------------------------------

            elif funcao.categoria == CategoriaFuncao.GESTAO:

                for experiencia in (experiencias or []):

                    ExperienciaProfissional.objects.create(
                        atribuicao=atribuicao,
                        **experiencia
                    )


            # ---------------------------------------------------------
            # HISTÓRICO DE VÍNCULO FORMAL
            #
            # Comum a Docente e Gestão.
            # Nunca aplicado a Discente.
            # ---------------------------------------------------------

            if funcao.categoria in (
                CategoriaFuncao.DOCENTE,
                CategoriaFuncao.GESTAO
            ):

                for historico in (
                    historico_vinculo_formal or []
                ):

                    HistoricoVinculoFormal.objects.create(
                        atribuicao=atribuicao,
                        **historico
                    )


            # ---------------------------------------------------------
            # PENDÊNCIAS
            #
            # Universal — aplicável a qualquer categoria.
            # ---------------------------------------------------------

            for pendencia in (pendencias or []):

                PendenciaCadastro.objects.create(
                    atribuicao=atribuicao,
                    **pendencia
                )


        return pessoa, atribuicao, dados_docente


# =============================================================
# DOCENTE — CAPACIDADES / DISCIPLINAS
# =============================================================

class PreencherRequisitosEDisciplinasDocenteService:
    """
    SRP: completa o cadastro de um Docente já existente — Disciplinas
    Habilitadas/Capacidade (seção 7 da FE 008) — etapa que só pode acontecer
    depois que as Formações (tabelas 3-5) já estão salvas, já que a
    comprovação de Capacidade referencia uma Formação existente.

    NOTA (02/09/2026): 'dados_requisitos' (experiencia_docente_comprovada /
    formacao_especifica_comprobatoria) é código desatualizado — esses campos
    não existem mais em DadosDocente; os Requisitos de Contratação (RBAC 141)
    hoje moram em AtribuicaoFuncao.requisito_contratacao/documento_
    comprobatorio, coletados direto no cadastro inicial ou editados via
    EditarRequisitoContratacaoView. Este Service nunca chegou a ser
    conectado a nenhuma tela (a tela de Requisitos foi removida na Etapa B).
    Marcado no Backlog para limpeza — 'dados_requisitos' fica sem uso real
    até essa limpeza acontecer.
    """

    def executar(
        self,
        dados_docente,
        dados_requisitos: dict,
        capacidades: list
    ):

        from .models import Capacidade

        with transaction.atomic():

            for capacidade in (capacidades or []):

                Capacidade.objects.create(
                    dados_docente=dados_docente,
                    **capacidade
                )

        return dados_docente


# =============================================================
# CEP
# =============================================================

class BuscarEnderecoPorCepService:
    """
    DIP: depende da abstração (porta),
    não da implementação concreta (ViaCEP).
    """

    def __init__(self, cliente_cep=None):

        self.cliente_cep = (
            cliente_cep or ViaCepClient()
        )

    def executar(self, cep: str):

        return self.cliente_cep.buscar_endereco(
            cep
        )


# =============================================================
# ENCERRAMENTO DE VÍNCULO
# =============================================================

class EncerrarVinculoService:
    """
    Encerra qualquer AtribuicaoFuncao — Discente, Docente ou Gestão (docs/37,
    Etapa 0). Só situacao + data_fim: sem Ata aqui de propósito — a Ata de
    encerramento de um Discente vive em MatriculaTurma.ata_encerramento
    (módulo atribuicao), não em AtribuicaoFuncao. Usado tanto pelo botão
    manual (Docente/Gestão, e Discente fora do fluxo de turma) quanto pelo
    módulo atribuicao (encerramento individual ou em lote ao fechar Turma).
    """

    def executar(
        self,
        atribuicao_funcao,
        data_fim
    ):

        from .models import SituacaoAtribuicao

        atribuicao_funcao.situacao = (
            SituacaoAtribuicao.INATIVO
        )

        atribuicao_funcao.data_fim = data_fim

        atribuicao_funcao.save()

        return atribuicao_funcao


# =============================================================
# INICIAR TURMA
# =============================================================

class IniciarTurmaService:
    """
    PLANEJADA -> EM_ANDAMENTO. Chamado pelo módulo atribuicao ao "Finalizar
    Planejamento" (docs/37, seção 4.2). Turma.situacao só avança, nunca
    retrocede (exceto via Admin, fora deste Service).
    """

    def executar(
        self,
        turma
    ):

        from .models import SituacaoTurma

        if turma.situacao != SituacaoTurma.PLANEJADA:

            raise ValidationError(
                "Só é possível iniciar uma Turma que está Planejada."
            )

        turma.situacao = SituacaoTurma.EM_ANDAMENTO

        turma.save()

        return turma


# =============================================================
# CONCLUIR TURMA
# =============================================================

class ConcluirTurmaService:
    """
    EM_ANDAMENTO -> ENCERRADA. Chamado pelo módulo atribuicao no 2º clique de
    "Encerrar Turma" (docs/37, seção 4.4), só depois que ninguém mais está
    CURSANDO (validado do lado de atribuicao, antes de chamar este Service).
    """

    def executar(
        self,
        turma,
        data_encerramento
    ):

        from .models import SituacaoTurma

        if turma.situacao != SituacaoTurma.EM_ANDAMENTO:

            raise ValidationError(
                "Só é possível encerrar uma Turma que está Em Andamento."
            )

        turma.situacao = SituacaoTurma.ENCERRADA

        turma.data_encerramento = data_encerramento

        turma.save()

        return turma


# =============================================================
# OBTER OU CRIAR ATRIBUIÇÃO DISCENTE
# =============================================================

class ObterOuCriarAtribuicaoDiscenteService:
    """
    Usado pelo módulo atribuicao ao matricular uma Pessoa numa Turma
    regular ou extracurricular.

    Reaproveita uma AtribuicaoFuncao Discente ATIVA, caso já exista.

    Se não existir Discente ativo, poderá criar uma nova atribuição,
    desde que a Pessoa NÃO possua função ativa de Docente ou Gestão.

    Regra de exclusividade:

    - Discente ativo não acumula Docente ou Gestão.
    - Docente ou Gestão ativo não podem receber Discente.
    - Docente + Gestão é permitido.
    - Atribuições inativas não impedem uma nova atribuição Discente.
    - Uma atribuição antiga nunca é reaberta.
    """

    def executar(
        self,
        pessoa,
        data_inicio
    ):

        from django.utils import timezone

        from .models import (
            AtribuicaoFuncao,
            CategoriaFuncao,
            DadosDiscente,
            Funcao,
            SituacaoAtribuicao,
        )


        # ---------------------------------------------------------
        # VERIFICA SE JÁ EXISTE DISCENTE ATIVO
        # ---------------------------------------------------------
        #
        # Se existir, reutiliza essa mesma AtribuicaoFuncao.
        # Isso permite que o mesmo Discente participe de mais de
        # uma Turma usando o mesmo vínculo institucional.
        # ---------------------------------------------------------

        discente_ativo = pessoa.atribuicoes.filter(
            dados_discente__isnull=False,
            situacao=SituacaoAtribuicao.ATIVO,
        ).first()


        if discente_ativo:

            return discente_ativo


        # ---------------------------------------------------------
        # REGRA DE EXCLUSIVIDADE DO DISCENTE
        # ---------------------------------------------------------
        #
        # Neste ponto sabemos que a Pessoa NÃO possui Discente ativo.
        #
        # Agora verificamos se existe qualquer outra função ativa.
        #
        # Se houver Docente ou Gestão ativo, não podemos criar uma
        # nova atribuição Discente.
        # ---------------------------------------------------------

        possui_outra_funcao_ativa = (
            pessoa.atribuicoes
            .filter(
                situacao=SituacaoAtribuicao.ATIVO
            )
            .exclude(
                funcao__categoria=CategoriaFuncao.DISCENTE
            )
            .exists()
        )


        if possui_outra_funcao_ativa:

            raise ValidationError(
                "Esta pessoa já possui uma Função ativa de "
                "Docente ou Gestão e não pode ser cadastrada "
                "como Discente enquanto esse vínculo estiver ativo."
            )


        # ---------------------------------------------------------
        # LOCALIZA A FUNÇÃO DISCENTE
        # ---------------------------------------------------------

        funcao_discente = Funcao.objects.get(
            categoria=CategoriaFuncao.DISCENTE
        )


        # ---------------------------------------------------------
        # CRIA NOVA ATRIBUIÇÃO DISCENTE
        # ---------------------------------------------------------

        nova = AtribuicaoFuncao.objects.create(
            pessoa=pessoa,
            funcao=funcao_discente,
            situacao=SituacaoAtribuicao.ATIVO,
            data_inicio=(
                data_inicio
                or timezone.now().date()
            ),
        )


        # ---------------------------------------------------------
        # CRIA A EXTENSÃO DADOS DISCENTE
        # ---------------------------------------------------------

        DadosDiscente.objects.create(
            atribuicao=nova
        )


        return nova