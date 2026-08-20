"""
pessoas/services.py

Camada de Services: regras de negócio que envolvem mais de uma entidade,
ou que precisam de validação além do que o Model sozinho garante.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import FuncaoGestao, Habilitacao, FuncaoGestaoHabilitacao, TipoFuncaoGestao


class AssociarHabilitacaoService:
    """
    SRP: única responsabilidade é associar uma Habilitacao a uma FuncaoGestao,
    validando a invariante de domínio (só Coordenador pode ter Habilitação).
    """

    def executar(self, funcao_gestao: FuncaoGestao, habilitacao: Habilitacao) -> FuncaoGestaoHabilitacao:
        if funcao_gestao.tipo_funcao != TipoFuncaoGestao.COORDENADOR:
            raise ValidationError(
                f"Habilitação só pode ser associada a Coordenador. "
                f"Função informada: {funcao_gestao.get_tipo_funcao_display()}"
            )

        with transaction.atomic():
            return FuncaoGestaoHabilitacao.objects.create(
                funcao_gestao=funcao_gestao,
                habilitacao=habilitacao
            )