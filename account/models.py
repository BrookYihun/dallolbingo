from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=20,null=True)
    tel_id = models.CharField(max_length=50, null=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return self.user.username