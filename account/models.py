from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from agent.models import Agent

# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    account = models.DecimalField(max_digits=15, decimal_places=2)
    prepaid = models.BooleanField(default=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_earning = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    net_earning = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    min_stake = models.DecimalField(max_digits=10, decimal_places=0)
    cut_percentage = models.DecimalField(max_digits=5,decimal_places=2,default=0.2)
    cut_bouldery = models.IntegerField(default=100)
    backup_password = models.CharField(max_length=255,default="")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='agent', default=None)

    def __str__(self):
        return self.name
    
class UserGameCounter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_game_date = models.DateField(auto_now_add=True)
    game_counter = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - Game Counter: {self.game_counter}"

    def increment_game_counter(self):
        today = datetime.now().date()
        if self.last_game_date != today:
            self.game_counter = 1
            self.last_game_date = today
        else:
            self.game_counter += 1
        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patterns = models.JSONField(default=list)  # Stores selected patterns as a list
    display_info = models.BooleanField(default=True)  # Stores display toggle state

    def __str__(self):
        return f"{self.user.username} Profile"