from django.contrib import admin
from .models import (
    Pessoa, Disciplina, Capacidade, Funcao, AtribuicaoFuncao, DadosDiscente,
    DadosDocente, ExperienciaProfissional, VinculoFormal, HistoricoVinculoFormal,
    FormacaoDocente, PendenciaCadastro,
)


admin.site.register(Pessoa)
admin.site.register(Disciplina)
admin.site.register(Capacidade)
admin.site.register(Funcao)
admin.site.register(AtribuicaoFuncao)
admin.site.register(DadosDiscente)
admin.site.register(DadosDocente)
admin.site.register(ExperienciaProfissional)
admin.site.register(VinculoFormal)
admin.site.register(HistoricoVinculoFormal)
admin.site.register(FormacaoDocente)
admin.site.register(PendenciaCadastro)
