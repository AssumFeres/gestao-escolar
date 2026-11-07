import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cadastros', '0014_remove_atribuicaofuncao_ativo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatriculaTurma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_na_turma', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('CURSANDO', 'Cursando'), ('APROVADO', 'Aprovado'), ('RELOCADO', 'Relocado'),
                        ('TRANSFERIDO', 'Transferido'), ('REPROVADO', 'Reprovado'),
                        ('MATRICULA_EXCLUIDA', 'Matrícula Excluída'),
                    ],
                    default='CURSANDO', max_length=20,
                )),
                ('motivo_saida', models.CharField(
                    blank=True,
                    choices=[('ABANDONOU', 'Desistente - Abandonou'), ('SOLICITOU', 'Desistente - Solicitou')],
                    max_length=20,
                )),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True)),
                ('atribuicao_funcao', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT, related_name='matriculas_turma', to='cadastros.atribuicaofuncao'
                )),
                ('turma', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='cadastros.turma'
                )),
                ('ata_inicio', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                    related_name='+', to='cadastros.ata'
                )),
                ('ata_encerramento', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                    related_name='+', to='cadastros.ata'
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name='matriculaturma',
            constraint=models.UniqueConstraint(fields=('atribuicao_funcao', 'turma'), name='unique_atribuicao_por_turma'),
        ),
        migrations.AddConstraint(
            model_name='matriculaturma',
            constraint=models.UniqueConstraint(fields=('turma', 'numero_na_turma'), name='unique_numero_por_turma'),
        ),
    ]
