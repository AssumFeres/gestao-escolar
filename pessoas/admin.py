from django.contrib import admin
from .models import (
    Pessoa, VinculoDiscente, VinculoDocente, VinculoGestao,
    FuncaoGestao, Habilitacao, FuncaoGestaoHabilitacao,
    Disciplina, Capacidade, Funcao, AtribuicaoFuncao, DadosDiscente,
    DadosDocente,
)


admin.site.register(Pessoa)
admin.site.register(VinculoDiscente)
admin.site.register(VinculoDocente)
admin.site.register(VinculoGestao)
admin.site.register(FuncaoGestao)
admin.site.register(Habilitacao)
admin.site.register(FuncaoGestaoHabilitacao)
admin.site.register(Disciplina)
admin.site.register(Capacidade)
admin.site.register(Funcao)
admin.site.register(AtribuicaoFuncao)
admin.site.register(DadosDiscente)
admin.site.register(DadosDocente)
