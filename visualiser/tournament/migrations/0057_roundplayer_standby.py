# Generated by Django 2.2 on 2021-09-26 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0056_player_backstabbr_profile_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='roundplayer',
            name='standby',
            field=models.BooleanField(default=False, help_text='check if the player would prefer not to play this round'),
        ),
    ]
