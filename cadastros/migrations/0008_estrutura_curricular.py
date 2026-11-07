from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0007_remove_passaporte_autorizacao_de_dadosdiscente'),
    ]

    operations = [
        # --- Ajustes em Disciplina (docs/33) ---
        migrations.RemoveField(
            model_name='disciplina',
            name='carga_horaria',
        ),
        migrations.AddField(
            model_name='disciplina',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='disciplina',
            name='carga_horaria_programa_de_instrucao',
            field=models.DecimalField(
                decimal_places=2, max_digits=6,
                help_text='Valor fixo, definido no Programa de Instrução aprovado pela ANAC.',
                default=Decimal('0.00'),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='disciplina',
            name='carga_horaria_teorica',
            field=models.DecimalField(decimal_places=2, max_digits=6, default=Decimal('0.00')),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='disciplina',
            name='carga_horaria_pratica',
            field=models.DecimalField(decimal_places=2, max_digits=6, default=Decimal('0.00')),
            preserve_default=False,
        ),

        # --- ConteudoProgramatico (nova) ---
        migrations.CreateModel(
            name='ConteudoProgramatico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.PositiveSmallIntegerField()),
                ('descricao', models.TextField()),
                ('observacao', models.TextField(blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='conteudos_programaticos', to='cadastros.disciplina')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('disciplina', 'ordem'), name='unique_ordem_por_disciplina')],
            },
        ),

        # --- Modulo (nova) ---
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigla', models.CharField(max_length=3, unique=True, validators=[django.core.validators.RegexValidator(message='Sigla deve conter exatamente 3 letras maiúsculas (ex: CBA, PSO, TCX).', regex='^[A-Z]{3}$')])),
                ('ativo', models.BooleanField(default=True)),
                ('nome', models.CharField(max_length=150, unique=True)),
                ('descricao', models.TextField(blank=True)),
            ],
        ),

        # --- SubModulo (nova) ---
        migrations.CreateModel(
            name='SubModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigla', models.CharField(max_length=3, unique=True, validators=[django.core.validators.RegexValidator(message='Sigla deve conter exatamente 3 letras maiúsculas (ex: CBA, PSO, TCX).', regex='^[A-Z]{3}$')])),
                ('ativo', models.BooleanField(default=True)),
                ('nome', models.CharField(max_length=150)),
            ],
        ),

        # --- SubModuloDisciplina (tabela intermediária) ---
        migrations.CreateModel(
            name='SubModuloDisciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.PositiveSmallIntegerField()),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submodulos_vinculados', to='cadastros.disciplina')),
                ('submodulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='disciplinas_vinculadas', to='cadastros.submodulo')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('submodulo', 'disciplina'), name='unique_disciplina_por_submodulo'),
                    models.UniqueConstraint(fields=('submodulo', 'ordem'), name='unique_ordem_disciplina_por_submodulo'),
                ],
            },
        ),

        # --- ModuloSubModulo (tabela intermediária) ---
        migrations.CreateModel(
            name='ModuloSubModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.PositiveSmallIntegerField()),
                ('modulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submodulos_vinculados', to='cadastros.modulo')),
                ('submodulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='modulos_vinculados', to='cadastros.submodulo')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('modulo', 'submodulo'), name='unique_submodulo_por_modulo'),
                    models.UniqueConstraint(fields=('modulo', 'ordem'), name='unique_ordem_submodulo_por_modulo'),
                ],
            },
        ),

        # --- OfertaModulo (nova) ---
        migrations.CreateModel(
            name='OfertaModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano_letivo', models.PositiveSmallIntegerField()),
                ('data_inicio', models.DateField()),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('ativo', models.BooleanField(default=True)),
                ('observacao', models.TextField(blank=True)),
                ('modulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ofertas', to='cadastros.modulo')),
            ],
        ),

        # --- Turma (nova) ---
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('sigla', models.CharField(max_length=10)),
                ('periodo', models.CharField(choices=[('MATUTINO', 'Matutino'), ('VESPERTINO', 'Vespertino'), ('NOTURNO', 'Noturno')], max_length=20)),
                ('capacidade_maxima', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('situacao', models.CharField(choices=[('PLANEJADA', 'Planejada'), ('EM_ANDAMENTO', 'Em Andamento'), ('ENCERRADA', 'Encerrada')], default='PLANEJADA', max_length=20)),
                ('observacao', models.TextField(blank=True)),
                ('oferta_modulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='turmas', to='cadastros.ofertamodulo')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('oferta_modulo', 'sigla'), name='unique_sigla_por_oferta')],
            },
        ),

        # --- Ata (nova) ---
        migrations.CreateModel(
            name='Ata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20, unique=True)),
                ('tipo', models.CharField(choices=[('ORDINARIA', 'Ordinária'), ('EXTRAORDINARIA', 'Extraordinária')], max_length=20)),
                ('finalidade', models.CharField(choices=[('INICIO_VINCULO', 'Início de Vínculo'), ('TERMINO_VINCULO', 'Término de Vínculo'), ('ORIENTACAO', 'Orientação'), ('CONSELHO_ENSINO', 'Conselho de Ensino'), ('OUTRO', 'Outro')], max_length=20)),
                ('data', models.DateField()),
                ('assunto', models.CharField(blank=True, max_length=255)),
                ('observacao', models.TextField(blank=True)),
            ],
        ),
    ]
