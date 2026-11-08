from django import template
from django.utils.html import format_html


register = template.Library()


@register.simple_tag
def indicador_obrigatorio():
    return format_html('<abbr class="campo-obrigatorio" title="Obrigatório">{}</abbr>', '*')


@register.simple_tag
def rotulo_campo(campo):
    """Preserva o label/legend nativo do Django e sinaliza campos obrigatórios."""
    conteudo = campo.label
    if campo.field.required:
        conteudo = format_html('{} {}', campo.label, indicador_obrigatorio())
    renderizar = campo.legend_tag if campo.use_fieldset else campo.label_tag
    return renderizar(contents=conteudo)


@register.simple_tag
def possui_campos_obrigatorios(form):
    return any(campo.field.required and not campo.is_hidden for campo in form)


@register.simple_tag
def destino_erro(campo):
    if campo.is_hidden:
        return ''
    if campo.id_for_label:
        return campo.id_for_label
    # Grupos de opções não têm um único id_for_label; usar uma opção focável.
    for opcao in campo:
        if not opcao.data['attrs'].get('disabled'):
            return opcao.id_for_label
    return ''
