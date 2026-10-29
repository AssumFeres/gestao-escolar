from django.contrib import admin
from .models import MatriculaTurma

admin.site.register(MatriculaTurma)

from django.contrib import admin
from .models import RegistroInstrucao

@admin.register(RegistroInstrucao)
class RegistroInstrucaoAdmin(admin.ModelAdmin):
    # Escolha quais colunas vão aparecer na lista geral de registros
    list_display = ('instrutor', 'data_instrucao', 'tipo', 'carga_horaria')
    
    # Adicione filtros na lateral direita para facilitar a busca
    list_filter = ('tipo', 'data_instrucao')
    
    # Permita buscar por texto digitando o nome do instrutor ou conteúdo
    search_fields = ('instrutor__username', 'conteudo')
