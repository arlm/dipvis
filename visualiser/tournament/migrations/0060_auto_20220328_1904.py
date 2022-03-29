# Generated by Django 2.2 on 2022-03-29 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0059_auto_20211112_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='scoring_system',
            field=models.CharField(choices=[('Bangkok', 'Bangkok'), ('CDiplo 100', 'CDiplo 100'), ('CDiplo 80', 'CDiplo 80'), ('Carnage with dead equal', 'Carnage with dead equal'), ('Carnage with elimination order', 'Carnage with elimination order'), ('Center-count Carnage', 'Center-count Carnage'), ('Detour09', 'Detour09'), ('Draw size', 'Draw size'), ('ManorCon', 'ManorCon'), ('Maxonian', 'Maxonian'), ('Original ManorCon', 'Original ManorCon'), ('Solo or bust', 'Solo or bust'), ('Sum of Squares', 'Sum of Squares'), ('Tribute', 'Tribute'), ('Whipping', 'Whipping'), ('World Classic', 'World Classic')], help_text='How to calculate a score for one game', max_length=40, verbose_name='Game scoring system'),
        ),
        migrations.AlterField(
            model_name='roundplayer',
            name='game_count',
            field=models.PositiveIntegerField(default=1, help_text='number of games to play this round'),
        ),
    ]
