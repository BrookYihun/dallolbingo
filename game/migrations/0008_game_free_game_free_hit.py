# Generated by Django 4.2.3 on 2024-07-22 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_alter_game_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='free_hit',
            field=models.IntegerField(default=0),
        ),
    ]
