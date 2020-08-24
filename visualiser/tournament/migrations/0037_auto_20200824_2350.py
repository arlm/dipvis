# Generated by Django 2.1.2 on 2020-08-25 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0036_auto_20200818_2100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roundplayer',
            options={'ordering': ['player', 'the_round__start']},
        ),
        migrations.AddField(
            model_name='round',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='round',
            name='enable_check_in',
            field=models.BooleanField(default=False, verbose_name='Enable self-check-ins'),
        ),
    ]