from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from account.models import Account

# Create your models here.

class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20,default="")
    backup_password = models.CharField(max_length=255,default="")
    last_game_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=100,default=0,decimal_places=2)
    shop = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='shop', default=None)

    def __str__(self):
        return self.name

    def increment_balance(self,value):
        today = datetime.now().date()
        if self.last_game_date != today:
            self.balance = 0
            self.last_game_date = today
        else:
            self.balance += Decimal(value)
        self.save()
    
    def decrement_balance(self,value):
        today = datetime.now().date()
        if self.last_game_date != today:
            self.balance = 0
            self.last_game_date = today
        else:
            self.balance -= Decimal(value)
        self.save()