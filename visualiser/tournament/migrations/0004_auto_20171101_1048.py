# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 17:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0003_auto_20171025_1549'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PlayerRanking',
            new_name='PlayerTournamentRanking',
        ),
        migrations.RunSQL(
            'DROP INDEX tournament_playerranking_player_id_8845f620'
        ),
    ]