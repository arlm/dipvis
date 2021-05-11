# Generated by Django 2.1.7 on 2021-05-11 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0051_auto_20210508_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='round_scoring_system',
            field=models.CharField(choices=[('Add all game scores', 'Add all game scores'), ('Best game counts', 'Best game counts'), ('Best game counts. Sitters get 4005', 'Best game counts. Sitters get 4005'), ('Best game counts. Sitters get 4005 once', 'Best game counts. Sitters get 4005 once')], help_text='How to combine game scores into a round score', max_length=40),
        ),
    ]
