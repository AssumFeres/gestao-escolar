import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0009_remove_turma_capacidade_maxima'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtaPessoa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ata', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pessoas_vinculadas', to='cadastros.ata')),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='atas_vinculadas', to='cadastros.pessoa')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('ata', 'pessoa'), name='unique_pessoa_por_ata')],
            },
        ),
    ]
