# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-18 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='name',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='playergameresult',
            name='tournament_name',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='playerranking',
            name='tournament',
            field=models.CharField(max_length=40),
        ),
    ]