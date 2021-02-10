# Generated by Django 2.2.16 on 2021-02-10 03:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0044_auto_20210207_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='powerbid',
            name='the_round',
            field=models.ForeignKey(default=30, on_delete=django.db.models.deletion.CASCADE, to='tournament.Round', verbose_name='round'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tournament',
            name='power_assignment',
            field=models.CharField(choices=[('A', 'Minimising playing the same power'), ('M', 'Manually by TD or at the board'), ('P', 'Using player preferences and ranking'), ('B', 'Blind auction (separate funds for each round)'), ('T', 'Blind auction (single pool for all rounds)')], default='M', max_length=1, verbose_name='How powers are assigned'),
        ),
        migrations.AlterUniqueTogether(
            name='powerbid',
            unique_together={('player', 'bid', 'the_round')},
        ),
    ]