from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    account = models.DecimalField(max_digits=15, decimal_places=2)
    prepaid = models.BooleanField(default=False)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    backup_password = models.CharField(max_length=255,default="")
    privilege = models.BooleanField(default=False)
    min_stake = models.DecimalField(max_digits=10, decimal_places=0,default=20)

    def __str__(self):
        return self.name