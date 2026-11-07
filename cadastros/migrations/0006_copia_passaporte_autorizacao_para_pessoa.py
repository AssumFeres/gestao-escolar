from django.db import migrations


def copiar_passaporte_para_pessoa(apps, schema_editor):
    """
    Copia o dado já existente de DadosDiscente.passaporte/autorizacao_permanencia
    para a Pessoa correspondente, antes desses campos serem removidos de
    DadosDiscente (migration 0007) — parte da lacuna aprovada na auditoria de
    campos FE 007/FE 008/FOP 402 de 03/09/2026 (ver docs/28). Só sobrescreve
    Pessoa se ela ainda não tiver o dado preenchido (evita sobrepor algo já
    corrigido manualmente por outro caminho).
    """
    DadosDiscente = apps.get_model('cadastros', 'DadosDiscente')
    for dd in DadosDiscente.objects.select_related('atribuicao__pessoa').all():
        pessoa = dd.atribuicao.pessoa
        alterou = False
        if dd.passaporte and not pessoa.passaporte:
            pessoa.passaporte = dd.passaporte
            alterou = True
        if dd.autorizacao_permanencia and not pessoa.autorizacao_permanencia:
            pessoa.autorizacao_permanencia = dd.autorizacao_permanencia
            alterou = True
        if alterou:
            pessoa.save()


def reverter(apps, schema_editor):
    # Migration reversível só estruturalmente — não desfaz a cópia de dado
    # (o dado pode já ter sido editado em Pessoa por outro caminho depois).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0005_pessoa_autorizacao_permanencia_pessoa_email_2_and_more'),
    ]

    operations = [
        migrations.RunPython(copiar_passaporte_para_pessoa, reverter),
    ]
