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
    jackpot_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of each prize to contribute to jackpot (e.g., 2.00 for 2%)"
    )
    jackpot_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Jackpot threshold amount (in birr) to trigger payout"
    )
    jackpot_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Current accumulated jackpot pool"
    )


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


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.BooleanField(default=False)  # False = pending, True = completed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit {self.id} - {self.user.username} - {self.amount} ({'Done' if self.status else 'Pending'})"


class Profile(models.Model):
    CARTELA_CHOICES = [
        ("super", "Super"),
        ("dallol", "Dallol"),
        ("africa", "Africa"),
        ("hummer", "Hummer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_info = models.BooleanField(default=True)  # Stores display toggle state
    cartela = models.CharField(
        max_length=20,
        choices=CARTELA_CHOICES,
        default="dallol",  # You can change the default if needed
    )

    def __str__(self):
        return f"{self.user.username} Profile"