# Generated by Django 2.2.16 on 2021-02-06 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0042_auto_20210205_1846'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='powerbid',
            options={'ordering': ['player', 'power']},
        ),
    ]
