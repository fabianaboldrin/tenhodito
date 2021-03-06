# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-21 00:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalIndexTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('is_main', models.BooleanField(default=False)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposalindextheme_related', to='application.Analysis')),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='application.ProposalIndex')),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposal_indexes', to='application.Theme')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpeechIndexTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('is_main', models.BooleanField(default=False)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='speechindextheme_related', to='application.Analysis')),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='application.SpeechIndex')),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='speech_indexes', to='application.Theme')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='indextheme',
            name='analysis',
        ),
        migrations.RemoveField(
            model_name='indextheme',
            name='index',
        ),
        migrations.RemoveField(
            model_name='indextheme',
            name='theme',
        ),
        migrations.DeleteModel(
            name='IndexTheme',
        ),
    ]
