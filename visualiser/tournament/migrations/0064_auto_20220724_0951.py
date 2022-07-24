# Generated by Django 2.2 on 2022-07-24 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0063_auto_20220415_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='notes',
            field=models.CharField(blank=True, help_text='Will be included in board call emails and game page', max_length=120, verbose_name='URL/Notes'),
        ),
    ]
