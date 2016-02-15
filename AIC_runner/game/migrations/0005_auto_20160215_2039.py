# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20160210_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='DockerContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=50, verbose_name='tag')),
                ('description', models.TextField(verbose_name='description')),
                ('dockerfile_src', models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'docker/dockerfiles', null=True, verbose_name='dockerfile source', blank=True)),
                ('version', models.PositiveSmallIntegerField(default=1, verbose_name='version')),
                ('cores', models.CommaSeparatedIntegerField(default=[1024], max_length=512, verbose_name='cores')),
                ('memory', models.PositiveIntegerField(default=104857600, verbose_name='memory')),
                ('swap', models.PositiveIntegerField(default=0, verbose_name='swap')),
                ('build_log', models.TextField(verbose_name='build log', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgrammingLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='title')),
                ('compile_container', models.ForeignKey(related_name='+', verbose_name='compile container', blank=True, to='game.DockerContainer', null=True)),
                ('execute_container', models.ForeignKey(related_name='+', verbose_name='execute container', blank=True, to='game.DockerContainer', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='game',
            name='config',
        ),
        migrations.AddField(
            model_name='competition',
            name='composer',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'docker/composers', null=True, verbose_name='docker composer', blank=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='players_per_game',
            field=models.PositiveIntegerField(default=2, verbose_name='number of players per game', blank=True),
        ),
        migrations.AddField(
            model_name='game',
            name='game_type',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='game type', choices=[(0, 'manual'), (1, 'friendly'), (2, 'qualifications'), (3, 'finals')]),
        ),
        migrations.AddField(
            model_name='competition',
            name='additional_containers',
            field=models.ManyToManyField(related_name='_competition_additional_containers_+', verbose_name='additional containers', to='game.DockerContainer', blank=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='server',
            field=models.ForeignKey(verbose_name='server container', blank=True, to='game.DockerContainer', null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='supported_langs',
            field=models.ManyToManyField(to='game.ProgrammingLanguage', verbose_name='supported languages', blank=True),
        ),
    ]
