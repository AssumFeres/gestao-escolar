from django.db import migrations, models


def normalizar_situacao_a_partir_de_ativo(apps, schema_editor):
    """
    'situacao' sempre foi texto livre, nunca editável por nenhuma tela — na
    prática, todo registro tem o valor literal "ATIVO" (initial do Form,
    nunca alterado). O campo 'ativo' (booleano), também nunca editável por
    tela, é o sinal mais confiável — usamos ele para decidir o valor final.
    """
    AtribuicaoFuncao = apps.get_model('cadastros', 'AtribuicaoFuncao')
    AtribuicaoFuncao.objects.filter(ativo=True).update(situacao='ATIVO')
    AtribuicaoFuncao.objects.filter(ativo=False).update(situacao='INATIVO')


def reverter(apps, schema_editor):
    # Reversível só estruturalmente — não desfaz a normalização de dado.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0012_modulo_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atribuicaofuncao',
            name='situacao',
            field=models.CharField(
                choices=[('ATIVO', 'Ativo'), ('INATIVO', 'Inativo')],
                default='ATIVO',
                max_length=10,
            ),
        ),
        migrations.RunPython(normalizar_situacao_a_partir_de_ativo, reverter),
    ]
