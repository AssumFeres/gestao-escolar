from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0010_atapessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ata',
            name='numero',
            field=models.CharField(
                blank=True, max_length=20,
                help_text='Deixe em branco para gerar automaticamente (3 dígitos/ano, por tipo).',
            ),
        ),
        migrations.AddConstraint(
            model_name='ata',
            constraint=models.UniqueConstraint(fields=('numero', 'tipo'), name='unique_numero_por_tipo'),
        ),
    ]
