from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0014_remove_atribuicaofuncao_ativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='turma',
            name='data_encerramento',
            field=models.DateField(blank=True, null=True),
        ),
    ]
