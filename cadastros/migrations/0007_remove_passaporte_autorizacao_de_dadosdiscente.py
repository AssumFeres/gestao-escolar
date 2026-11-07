from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0006_copia_passaporte_autorizacao_para_pessoa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dadosdiscente',
            name='passaporte',
        ),
        migrations.RemoveField(
            model_name='dadosdiscente',
            name='autorizacao_permanencia',
        ),
    ]
