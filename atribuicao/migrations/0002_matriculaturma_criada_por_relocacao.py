from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atribuicao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='matriculaturma',
            name='criada_por_relocacao',
            field=models.BooleanField(default=False),
        ),
    ]
