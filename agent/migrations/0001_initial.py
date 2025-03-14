# Generated by Django 4.2.19 on 2025-02-13 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=20)),
                ('account', models.DecimalField(decimal_places=2, max_digits=15)),
                ('prepaid', models.BooleanField(default=False)),
                ('percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('backup_password', models.CharField(default='', max_length=255)),
                ('privilege', models.BooleanField(default=False)),
                ('min_stake', models.DecimalField(decimal_places=0, default=20, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
