import json
from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    numbers = models.JSONField(default=dict)

    def __str__(self) -> str:
        return f"Bingo Card {self.id}"

class Game(models.Model):
    stake = models.CharField(default='20',max_length=50)
    numberofplayers = models.IntegerField(default=0)
    playerCard = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    played = models.CharField(max_length=50,default='STARTED')
    total_calls = models.IntegerField(default=0)
    cut_percentage = models.DecimalField(max_digits=5,default=0.2,decimal_places=2)
    winner_price = models.DecimalField(max_digits=100,default=0,decimal_places=2)
    shop_cut = models.DecimalField(max_digits=100,default=0,decimal_places=2)
    admin_cut = models.DecimalField(max_digits=100,default=0,decimal_places=2)
    winners = models.JSONField(default=list)
    free = models.BooleanField(default=False)
    free_hit = models.IntegerField(default=0)
    bonus = models.BooleanField(default=False)
    bonus_payed = models.IntegerField(default=0)
    

    def __str__(self) -> str:
        return f"Game number {self.id}"

class UserGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    game_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Game {self.game_number}"
    
class CashierGame(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    game = models.ForeignKey(Game,on_delete=models.CASCADE)
    
    collected = models.DecimalField(max_digits=100,default=0,decimal_places=2)
    pied = models.DecimalField(max_digits=100,default=0,decimal_places=2)

    def __str__(self) -> str:
        return f"{self.user.username} - Game {self.game.id}"
    
    # def get_card_numbers(self):
    #     # Load existing players
    #     players = json.loads(self.selected_players)
        
    #     return players
