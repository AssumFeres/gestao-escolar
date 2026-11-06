from django.contrib import admin
from .models import MatriculaTurma

admin.site.register(MatriculaTurma)

from django.contrib import admin
from .models import RegistroInstrucao

@admin.register(RegistroInstrucao)
class RegistroInstrucaoAdmin(admin.ModelAdmin):
    list_display = ('get_instrutor', 'atribuicao', 'data_instrucao', 'carga_horaria', 'tipo')
    # Adiciona filtros e buscas inteligentes para o painel não travar
    list_filter = ('tipo', 'data_instrucao')
    search_fields = ('atribuicao__instrutor__pessoa__nome_completo', 'conteudo_programatico')

    @admin.display(ordering='atribuicao__instrutor', description='Instrutor')
    def get_instrutor(self, obj):
        if obj.atribuicao and obj.atribuicao.instrutor:
            return obj.atribuicao.instrutor.pessoa.nome_completo
        return "Sem Instrutor"