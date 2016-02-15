# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import base.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20160215_2039'),
        ('base', '0015_auto_20160210_2247'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('made_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('accepted', models.NullBooleanField(verbose_name='state')),
                ('accept_time', models.DateTimeField(null=True, verbose_name='accept time', blank=True)),
                ('game', models.ForeignKey(to='game.Game', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='submit',
            name='pl',
        ),
        migrations.AddField(
            model_name='submit',
            name='compiled_code',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=base.models.team_compiled_code_directory_path, null=True, verbose_name='compiled code', blank=True),
        ),
        migrations.AddField(
            model_name='submit',
            name='lang',
            field=models.ForeignKey(verbose_name='programming language', to='game.ProgrammingLanguage', null=True),
        ),
        migrations.AddField(
            model_name='submit',
            name='submitter',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='will_come',
            field=models.PositiveSmallIntegerField(default=2, verbose_name='will come to site', choices=[(0, 'yes'), (1, 'no'), (2, 'not decided yet')]),
        ),
        migrations.AlterField(
            model_name='submit',
            name='code',
            field=models.FileField(upload_to=base.models.team_code_directory_path, storage=django.core.files.storage.FileSystemStorage(), verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='submit',
            name='compile_log_file',
            field=models.TextField(null=True, verbose_name='log file', blank=True),
        ),
        migrations.AddField(
            model_name='gamerequest',
            name='requestee',
            field=models.ForeignKey(related_name='+', verbose_name='requestee', to='base.Team'),
        ),
        migrations.AddField(
            model_name='gamerequest',
            name='requester',
            field=models.ForeignKey(related_name='+', verbose_name='requester', to='base.Team'),
        ),
    ]
