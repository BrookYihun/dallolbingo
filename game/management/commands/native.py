from django.core.management.base import BaseCommand
from django.utils.timezone import is_naive
from django.contrib.auth import get_user_model
from game.models import UserGame
from account.models import Agent, Account  # Adjust imports based on your project structure

User = get_user_model()

class Command(BaseCommand):
    help = "Check for UserGame records with naive created_at timestamps for all shops under Agent of User ID 25"

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(id=25)
            agent = Agent.objects.get(user=user)
            shops = Account.objects.filter(agent=agent)

            problematic_games = UserGame.objects.filter(user__in=[shop.user for shop in shops])

            naive_game_ids = [
                game.id for game in problematic_games if is_naive(game.created_at)
            ]

            if naive_game_ids:
                self.stdout.write("Naive timestamps found in games with IDs:")
                for game_id in naive_game_ids:
                    self.stdout.write(str(game_id))
            else:
                self.stdout.write("No naive timestamps found.")
        
        except User.DoesNotExist:
            self.stderr.write("User with ID 25 does not exist.")
        except Agent.DoesNotExist:
            self.stderr.write("No agent found for User ID 25.")
