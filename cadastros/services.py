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
            pessoa_existente = Pessoa.objects.filter(cpf=dados_pessoa['cpf']).first()

            # Duplicidade de RM/RA/CANAC — exclui a própria Pessoa existente
            # da checagem (senão o valor dela mesma "colidiria" com ela).
            campos_unicos = [
                ('registro_matricula', 'RM'),
                ('registro_aluno', 'RA'),
                ('codigo_anac', 'CANAC'),
            ]
            for campo, rotulo in campos_unicos:
                valor = dados_pessoa.get(campo)
                if not valor:
                    continue
                consulta = Pessoa.objects.filter(**{campo: valor})
                if pessoa_existente:
                    consulta = consulta.exclude(pk=pessoa_existente.pk)
                if consulta.exists():
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
                # Atualiza de verdade os campos da Pessoa existente com o
                # que veio do formulário — exceto 'cpf', que nunca muda.
                for campo, valor in dados_pessoa.items():
                    if campo != 'cpf':
                        setattr(pessoa, campo, valor)
                pessoa.save()

                # Corrigido em 07/09/2026 (docs/37, Etapa 0): antes checava só a
                # EXISTÊNCIA de uma AtribuicaoFuncao Discente, bloqueando até quem já
                # teve o vínculo encerrado há anos. Agora só bloqueia se houver uma
                # ATIVA — cada passagem da Pessoa pela EMCA como Discente é sua
                # própria AtribuicaoFuncao; um ex-aluno pode voltar como Discente
                # novo (nova AtribuicaoFuncao), sem reabrir a antiga.
                ja_e_discente_ativo = pessoa.atribuicoes.filter(
                    dados_discente__isnull=False, situacao='ATIVO'
                ).exists()
                if ja_e_discente_ativo:
                    raise ValidationError(
                        "Esta pessoa já possui a Função Discente ativa e não pode acumular outra Função."
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

    def executar(self, dados_docente, dados_requisitos: dict, capacidades: list):
        from .models import Capacidade

        with transaction.atomic():
            for capacidade in (capacidades or []):
                Capacidade.objects.create(dados_docente=dados_docente, **capacidade)

        return dados_docente


class BuscarEnderecoPorCepService:
    """DIP: depende da abstração (porta), não da implementação concreta (ViaCEP)."""

    def __init__(self, cliente_cep=None):
        self.cliente_cep = cliente_cep or ViaCepClient()

    def executar(self, cep: str):
        return self.cliente_cep.buscar_endereco(cep)


class EncerrarVinculoService:
    """
    Encerra qualquer AtribuicaoFuncao — Discente, Docente ou Gestão (docs/37,
    Etapa 0). Só situacao + data_fim: sem Ata aqui de propósito — a Ata de
    encerramento de um Discente vive em MatriculaTurma.ata_encerramento
    (módulo atribuicao), não em AtribuicaoFuncao. Usado tanto pelo botão
    manual (Docente/Gestão, e Discente fora do fluxo de turma) quanto pelo
    módulo atribuicao (encerramento individual ou em lote ao fechar Turma).
    """

    def executar(self, atribuicao_funcao, data_fim):
        from .models import SituacaoAtribuicao

        atribuicao_funcao.situacao = SituacaoAtribuicao.INATIVO
        atribuicao_funcao.data_fim = data_fim
        atribuicao_funcao.save()
        return atribuicao_funcao


class IniciarTurmaService:
    """
    PLANEJADA -> EM_ANDAMENTO. Chamado pelo módulo atribuicao ao "Finalizar
    Planejamento" (docs/37, seção 4.2). Turma.situacao só avança, nunca
    retrocede (exceto via Admin, fora deste Service).
    """

    def executar(self, turma):
        from .models import SituacaoTurma

        if turma.situacao != SituacaoTurma.PLANEJADA:
            raise ValidationError("Só é possível iniciar uma Turma que está Planejada.")
        turma.situacao = SituacaoTurma.EM_ANDAMENTO
        turma.save()
        return turma


class ObterOuCriarAtribuicaoDiscenteService:
    """
    Usado pelo módulo atribuicao ao matricular uma Pessoa numa Turma (regular
    ou extracurricular, docs/37 seção 7). Reaproveita a AtribuicaoFuncao
    Discente ATIVA existente, se houver — a mesma Pessoa pode acumular Turma
    regular + Extracurricular na mesma AtribuicaoFuncao. Se não houver
    nenhuma ativa (nunca foi Discente, ou só tem alguma já INATIVO no
    passado), cria uma nova, mínima — sem código de matrícula ANAC, sem
    nenhum requisito de aluno regular (já opcionais em DadosDiscente hoje).
    Nunca reabre uma AtribuicaoFuncao já INATIVO.
    """

    def executar(self, pessoa, data_inicio):
        from django.utils import timezone
        from .models import AtribuicaoFuncao, CategoriaFuncao, DadosDiscente, Funcao, SituacaoAtribuicao

        ativa = pessoa.atribuicoes.filter(dados_discente__isnull=False, situacao=SituacaoAtribuicao.ATIVO).first()
        if ativa:
            return ativa

        funcao_discente = Funcao.objects.get(categoria=CategoriaFuncao.DISCENTE)
        nova = AtribuicaoFuncao.objects.create(
            pessoa=pessoa,
            funcao=funcao_discente,
            situacao=SituacaoAtribuicao.ATIVO,
            data_inicio=data_inicio or timezone.now().date(),
        )
        DadosDiscente.objects.create(atribuicao=nova)
        return nova
