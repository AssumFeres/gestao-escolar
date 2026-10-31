from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0011_ata_numero_unique_por_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulo',
            name='categoria',
            field=models.CharField(
                choices=[('BASICO', 'Básico'), ('ESPECIALIZADO', 'Especializado'), ('EXTRACURRICULAR', 'Extracurricular')],
                max_length=20,
                default='BASICO',
            ),
            preserve_default=False,
        ),
    ]
