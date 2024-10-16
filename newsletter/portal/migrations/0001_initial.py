# Generated by Django 5.0.3 on 2024-04-01 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InfosProfissao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_profissao', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qtd_acessos', models.IntegerField()),
                ('data_ultimo_acesso', models.DateField()),
                ('esta_logado', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_newsletter', models.CharField(max_length=255)),
                ('link_newsletter', models.URLField()),
                ('titulo_materia_chamariz', models.CharField(max_length=255)),
                ('materia_chamativa', models.TextField()),
                ('qtd_inscritos', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('data_nascimento', models.DateField()),
                ('data_inscricao', models.DateField()),
                ('email', models.EmailField(max_length=254)),
                ('profissao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal.infosprofissao')),
            ],
        ),
        migrations.CreateModel(
            name='InscricaoNewsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inscricao', models.DateField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.cliente')),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.newsletter')),
            ],
        ),
        migrations.CreateModel(
            name='NewsletterProfissao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.newsletter')),
                ('profissao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.infosprofissao')),
            ],
        ),
        migrations.CreateModel(
            name='VagaEmprego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_vaga', models.CharField(max_length=255)),
                ('salario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descricao_vaga', models.TextField()),
                ('link_vaga', models.URLField()),
                ('data_publicacao', models.DateField()),
                ('profissao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal.infosprofissao')),
            ],
        ),
    ]
