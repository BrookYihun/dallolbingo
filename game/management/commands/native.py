from django.core.management.base import BaseCommand
from django.utils.timezone import is_naive
from django.contrib.auth import get_user_model
from game.models import UserGame, Game
from account.models import Agent, Account, UserGameCounter  # Adjust imports based on your project structure

User = get_user_model()

class Command(BaseCommand):
    help = "Check for UserGame records with naive created_at timestamps for all shops under Agent of User ID 25"

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(id=25)

            today = timezone.now().date()
            agent = Agent.objects.get(user=request.user)
            
            if agent is not None:
                shops = Account.objects.filter(agent=agent)
                shops_stat = []
                total_agent_earning = 0
                today_agent_earning = 0
        
                for shop in shops:
                    shop_stat = {}
                    total_games_played_today = 0
                    total_games_played = 0
                    today_earning = 0
                    net_today = 0
        
                    game_counter, created = UserGameCounter.objects.get_or_create(user=shop.user)
                    total_games_played_today += game_counter.game_counter if game_counter.last_game_date == today else 0
                    userGame = UserGame.objects.filter(user=shop.user)
                    total_games_played = len(userGame)
                    shop_stat['account'] = round(float(shop.account),2)
                    shop_stat['total_games_played_today'] = total_games_played_today
                    shop_stat['total_games_played'] = total_games_played
                    shop_stat['name'] = shop.name
                    shop_stat['id'] = shop.user.id
                    shop_stat['percentage'] = shop.percentage
                    shop_stat['prepaid'] = shop.prepaid
                    shop_stat['cut_percentage'] = shop.cut_percentage
                    shop_stat['cut_boundary'] = shop.cut_bouldery
                    today_game_obj = UserGame.objects.filter(game__created_at__date=today,user=shop.user)
        
                    for game in today_game_obj:
                        print(game.id)
                        today_earning+=float(game.game.shop_cut)
                        net_today+=(float(game.game.shop_cut)-float(game.game.admin_cut))
        
                    if shop.user.is_active:
                        shop_stat['active']='Deactivate'
                    else:
                        shop_stat['active']='Activate'
        
                    shop_stat['today_earning'] = round(today_earning,2)
                    today_agent_earning += today_earning
                    shop_stat['total_earning'] = round(shop.total_earning,2)
                    total_agent_earning += shop.total_earning
                    
                    shops_stat.append(shop_stat)
        
                agent_data = {
                    'account': agent.account,
                    'name': agent.name,
                    'privilege': agent.privilege,
                    'min_stake': agent.min_stake
                    # Add other fields as needed
                }
        
                context = {
                    'shops_stat':shops_stat,
                    'agent':agent_data,
                    'num_shops': len(shops),
                    'total_earning': round(total_agent_earning,2),
                    'today_earning': round(today_agent_earning,2)
                }
                print(context)
            
            context = {'message':'ERROR'}
            print(context)
        except User.DoesNotExist:
            self.stderr.write("User with ID 25 does not exist.")
        except Agent.DoesNotExist:
            self.stderr.write("No agent found for User ID 25.")
