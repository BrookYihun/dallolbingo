# Generated by Django 4.2.3 on 2024-07-22 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_account_backup_password_alter_account_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='cut_bouldery',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='account',
            name='cut_percentage',
            field=models.DecimalField(decimal_places=2, default=0.2, max_digits=5),
        ),
    ]
