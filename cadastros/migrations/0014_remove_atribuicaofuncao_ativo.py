from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0013_atribuicaofuncao_situacao_choices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atribuicaofuncao',
            name='ativo',
        ),
    ]
