from django.contrib import admin
from .models import (
    Pessoa, Disciplina, Capacidade, Funcao, AtribuicaoFuncao, DadosDiscente,
    DadosDocente, ExperienciaProfissional, VinculoFormal, HistoricoVinculoFormal,
    FormacaoDocente, PendenciaCadastro,
    ConteudoProgramatico, Modulo, SubModulo, SubModuloDisciplina, ModuloSubModulo,
    OfertaModulo, Turma, Ata,
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

# Estrutura curricular (docs/33, 05/09/2026) — catálogos Admin-only por enquanto,
# mesmo padrão simples dos demais acima, sem ModelAdmin customizado.
admin.site.register(ConteudoProgramatico)
admin.site.register(Modulo)
admin.site.register(SubModulo)
admin.site.register(SubModuloDisciplina)
admin.site.register(ModuloSubModulo)
admin.site.register(OfertaModulo)
admin.site.register(Turma)
admin.site.register(Ata)
