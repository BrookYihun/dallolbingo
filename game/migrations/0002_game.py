# Generated by Django 4.2.3 on 2024-02-24 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stake', models.CharField(default='20', max_length=50)),
                ('numberofplayers', models.IntegerField(default=0)),
                ('playerCard', models.JSONField(default='[]')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('played', models.CharField(default='Created', max_length=50)),
                ('total_calls', models.IntegerField(default=0)),
                ('called_numbers', models.JSONField(default=[0])),
                ('winner_price', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('admin_cut', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
            ],
        ),
    ]
