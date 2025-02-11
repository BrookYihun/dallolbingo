from datetime import datetime, timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import models

from account.models import Account, UserGameCounter
from agent.models import Agent
from cashier.models import Cashier
from game.models import UserGame
# Create your views here.

@login_required
def agent_index_view(request):
    agent = Agent.objects.get(user=request.user)
    
    if agent is not None:
        return render(request,'agent/index.html',{'agent':agent})
    
    return redirect('index')

@login_required
def get_shop_stat(request):
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

        return JsonResponse(context)
    
    context = {'message':'ERROR'}
    return JsonResponse(context)


@login_required
def admin_get_shop_stat(request,id):
    today = timezone.now().date()
    user = User.objects.get(id=int(id))
    agent = Agent.objects.get(user=user)
    
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

        return JsonResponse(context)
    
    context = {'message':'ERROR'}
    return JsonResponse(context)

@login_required
def get_agent_stat(request):
    if request.user.is_superuser:

        today = timezone.now().date()
        agents = Agent.objects.all()
        total_shops = 0
        total_earning = 0
        today_earning = 0
        agents_stat = []

        for agent in agents:
            total_earning_agent = 0
            today_earning_agent = 0
            today_game_agent = 0
            agent_stat = {}
            shops = Account.objects.filter(agent=agent)

            for shop in shops:

                game_counter, created = UserGameCounter.objects.get_or_create(user=shop.user)
                today_game_agent += game_counter.game_counter if game_counter.last_game_date == today else 0
                userGame = UserGame.objects.filter(game__created_at__date=today,user=shop.user)
                for game in userGame:
                    today_earning_agent+=float(game.game.admin_cut)

                total_earning_agent += shop.total_earning * shop.percentage

            agent_stat['name'] = agent.name
            agent_stat['percentage'] = agent.percentage
            agent_stat['prepaid'] = agent.prepaid
            agent_stat['privilege'] = agent.privilege
            agent_stat['id'] = agent.user.id
            agent_stat['account'] = agent.account
            agent_stat['total_shops'] = len(shops)
            agent_stat['total_earning'] = round(total_earning_agent,2)
            agent_stat['total_net'] = round(total_earning_agent - (total_earning_agent * agent.percentage),2)
            agent_stat['today_game'] = today_game_agent
            agent_stat['today_earning'] = round(today_earning_agent,2)
            if agent.user.is_active:
                agent_stat['active']='Deactivate'
            else:
                agent_stat['active']='Activate'

            total_shops += len(shops)
            total_earning += (total_earning_agent * agent.percentage)
            today_earning += today_earning_agent * float(agent.percentage)

            agents_stat.append(agent_stat)

        context = {
            'agents_stat':agents_stat,
            'num_shops': total_shops,
            'num_agent': len(agents),
            'total_earning': round(total_earning,2),
            'today_earning': round(today_earning,2)
        }

        return JsonResponse(context)
    else:
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
            shop_stat['cut_percentage'] = shop.cut_percentage
            shop_stat['cut_boundary'] = shop.cut_bouldery
            shop_stat['prepaid'] = shop.prepaid
            today_game_obj = UserGame.objects.filter(game__created_at__date=today,user=shop.user)

            for game in today_game_obj:
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

        return JsonResponse(context)
    context = {'message':'ERROR'}
    return JsonResponse(context)

@login_required
def get_shop_stat_filter(request):
    today = timezone.now().date()
    selected_date = request.GET.get('datefilter', None)
    if selected_date:
        start_date_str, end_date_str = selected_date.split(' - ')
        # Convert the date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y') + timedelta(days=1) - timedelta(seconds=1)
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
                userGame = UserGame.objects.filter(
                    user=shop.user,
                    game__created_at__gte=start_date,
                    game__created_at__lte=end_date
                )
                total_games_played = len(userGame)
                shop_stat['account'] = round(float(shop.account),2)
                shop_stat['total_games_played_today'] = total_games_played_today
                shop_stat['total_games_played'] = total_games_played
                shop_stat['name'] = shop.name
                shop_stat['id'] = shop.user.id
                shop_stat['percentage'] = shop.percentage
                shop_stat['cut_percentage'] = shop.cut_percentage
                shop_stat['cut_boundary'] = shop.cut_bouldery
                shop_stat['prepaid'] = shop.prepaid
                tot_ern = 0
                for game in userGame:
                    start_date_obj = timezone.make_aware(start_date, game.game.created_at.tzinfo)
                    end_date_obj = timezone.make_aware(end_date, game.game.created_at.tzinfo)
                    end_date_obj += timedelta(days=1)  # Include games on the end date
                    if game.game.created_at.date() == today:
                        today_earning+=float(game.game.shop_cut)
                        net_today+=(float(game.game.shop_cut)-float(game.game.admin_cut))
                    if game.game.created_at >= start_date_obj and game.game.created_at <= end_date_obj:
                        tot_ern += round(game.game.shop_cut,2)
                        total_agent_earning += round(game.game.shop_cut,2)
                if shop.user.is_active:
                    shop_stat['active']='Deactivate'
                else:
                    shop_stat['active']='Activate'
                shop_stat['total_earning'] = tot_ern
                shop_stat['today_earning'] = round(today_earning,2)
                today_agent_earning += today_earning
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

            return JsonResponse(context)
    else:
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
                shop_stat['cut_percentage'] = shop.cut_percentage
                shop_stat['cut_boundary'] = shop.cut_bouldery
                shop_stat['prepaid'] = shop.prepaid
                today_game_obj = UserGame.objects.filter(game__created_at__date=today,user=shop.user)

                for game in today_game_obj:
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

            return JsonResponse(context)

    context = {'message':'ERROR'}
    return JsonResponse(context)

@login_required
def admin_get_shop_stat_filter(request,id):
    today = timezone.now().date()
    selected_date = request.GET['datefilter']
    if selected_date:
        start_date_str, end_date_str = selected_date.split(' - ')
        # Convert the date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y') + timedelta(days=1) - timedelta(seconds=1)
        user = User.objects.get(id=int(id))
        agent = Agent.objects.get(user=user)
        
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
                userGame = UserGame.objects.filter(
                    user=shop.user,
                    game__created_at__gte=start_date,
                    game__created_at__lte=end_date
                )
                total_games_played = len(userGame)
                shop_stat['account'] = round(float(shop.account),2)
                shop_stat['total_games_played_today'] = total_games_played_today
                shop_stat['total_games_played'] = total_games_played
                shop_stat['name'] = shop.name
                shop_stat['id'] = shop.user.id
                shop_stat['percentage'] = shop.percentage
                shop_stat['cut_percentage'] = shop.cut_percentage
                shop_stat['cut_boundary'] = shop.cut_bouldery
                shop_stat['prepaid'] = shop.prepaid
                tot_ern = 0
                for game in userGame:
                    start_date_obj = timezone.make_aware(start_date, game.game.created_at.tzinfo)
                    end_date_obj = timezone.make_aware(end_date, game.game.created_at.tzinfo)
                    end_date_obj += timedelta(days=1)  # Include games on the end date
                    if game.game.created_at.date() == today:
                        today_earning+=float(game.game.shop_cut)
                        net_today+=(float(game.game.shop_cut)-float(game.game.admin_cut))
                    if game.game.created_at >= start_date_obj and game.game.created_at <= end_date_obj:
                        tot_ern += round(game.game.shop_cut,2)
                        total_agent_earning += round(game.game.shop_cut,2)
                if shop.user.is_active:
                    shop_stat['active']='Deactivate'
                else:
                    shop_stat['active']='Activate'
                shop_stat['total_earning'] = tot_ern
                shop_stat['today_earning'] = round(today_earning,2)
                today_agent_earning += today_earning
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

            return JsonResponse(context)
    else:
        today = timezone.now().date()
        user = User.objects.get(id=int(id))
        agent = Agent.objects.get(user=user)
        
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
                shop_stat['cut_percentage'] = shop.cut_percentage
                shop_stat['cut_boundary'] = shop.cut_bouldery
                shop_stat['prepaid'] = shop.prepaid
                today_game_obj = UserGame.objects.filter(game__created_at__date=today,user=shop.user)

                for game in today_game_obj:
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

            return JsonResponse(context)
    context = {'message':'ERROR'}
    return JsonResponse(context)

@csrf_exempt
@login_required
def add_shop(request):
    agent = Agent.objects.get(user=request.user)
    if agent is not None:
        if request.method == 'GET':
            try:
                name = request.GET['name']
                user_name = request.GET['user_name']
                password = request.GET['password']
                phone_number = request.GET['phone_number']
                percentage = request.GET['percentage']
                min_stake = request.GET['min_stake']
                

                user = User.objects.create_user(username=user_name, email=user_name+'@goldenbingos.com', password=password)
                user.save()

                acc = Account.objects.create(
                    user=user,
                    name=name,
                    phone_number=phone_number,
                    account=Decimal(0),
                    percentage=Decimal(percentage),
                    min_stake=Decimal(min_stake),
                    backup_password=password,
                    agent=agent
                )
                if agent.privilege:
                    prepaid = request.GET.get('prepaid') == 'on'
                    cut_percentage = request.GET.get('cut_percentage')
                    cut_boundary = request.GET.get('cut_boundary')
                    acc.cut_percentage = cut_percentage
                    acc.prepaid = prepaid
                    acc.cut_bouldery = cut_boundary

                acc.save()

                userGameCounter = UserGameCounter.objects.create(
                    user=user,
                    game_counter=0
                )
                userGameCounter.save()

                cashier_user = User.objects.create_user(username=user_name+"_main_cashier", email=user_name+'_main_cashier@goldenbingos.com', password=password)
                cashier_user.save()

                cashier = Cashier.objects.create(
                    user=cashier_user,
                    name=user_name+"_main_cashier",
                    shop=acc
                )
                cashier.save()

                context={'message':'Successfuly added shop '+acc.name}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('agent_index')
    
    return redirect('index')

@csrf_exempt
@login_required
def activate_deactivate_view(request):
    agent = Agent.objects.get(user=request.user)
    if agent is not None:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('user')
                user = User.objects.get(id=int(user_id))
                if user.is_active:
                    user.is_active = False
                else:
                    user.is_active = True

                user.save()

                context={'message':'Successfully changed shop '}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('agent_index')
    
    return redirect('index')
            

@csrf_exempt
@login_required
def get_shop_info(request):
    agent = Agent.objects.get(user=request.user)
    if agent is not None:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('user')
                user = User.objects.get(id=int(user_id))

                acc = Account.objects.get(user=user)
                shop_stat = {}
                
                shop_stat['account'] = round(float(acc.account),2)
                shop_stat['name'] = acc.name
                shop_stat['percentage'] = acc.percentage
                if acc.prepaid:
                    shop_stat['prepaid'] = 'checked'
                else:
                    shop_stat['prepaid'] = ''
                shop_stat['phone_number'] = acc.phone_number
                shop_stat['user_name'] = user.username
                shop_stat['password'] = acc.backup_password
                shop_stat['min_stake'] = acc.min_stake
                shop_stat['cut_percentage'] = acc.cut_percentage
                shop_stat['cut_boundary'] = acc.cut_bouldery

                agent_data = {
                    'account': agent.account,
                    'name': agent.name,
                    'privilege': agent.privilege,
                    'min_stake': agent.min_stake
                    # Add other fields as needed
                }

                context = {
                    'shop_stat':shop_stat,
                    'agent':agent_data,
                }

                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('agent_index')
    
    return redirect('index')

@csrf_exempt
@login_required
def add_balance(request):
    agent = Agent.objects.get(user=request.user)
    if agent is not None:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('id')
                user = User.objects.get(id=int(user_id))
                acc = Account.objects.get(user=user)
                balance = request.GET.get('account')
                if agent.account >= Decimal(balance) and agent.prepaid:
                    acc.account += Decimal(balance)
                    agent.account -= Decimal(balance)
                    agent.save()
                    acc.save()
                    context={'message':'Successfully added balance to shop '}
                elif agent.prepaid == False:
                    acc.account += Decimal(balance)
                    agent.account -= Decimal(balance)
                    agent.save()
                    acc.save()
                    context={'message':'Successfully added balance to shop '}
                else:
                    context={'message':'Insufficient balance!!'}

                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('agent_index')
    
    return redirect('index')

@csrf_exempt
@login_required
def edit_shop(request):
    agent = Agent.objects.get(user=request.user)
    if agent is not None:
        if request.method == 'GET':
            try:
                user_id = request.GET['id']
                name = request.GET['name']
                user_name = request.GET['user_name']
                password = request.GET['password']
                phone_number = request.GET['phone_number']
                percentage = request.GET['percentage']
                min_stake = request.GET['min_stake']
                prepaid = request.GET.get('prepaid') == 'on'

                user = User.objects.get(id=int(user_id))
                user.username = user_name
                user.set_password(password)
                user.save()

                acc = Account.objects.get(user=user)
                acc.name=name
                acc.backup_password = password
                acc.phone_number = phone_number
                acc.percentage = percentage
                acc.min_stake = min_stake
                if agent.privilege:
                    prepaid = request.GET.get('prepaid') == 'on'
                    cut_percentage = request.GET.get('cut_percentage')
                    cut_boundary = request.GET.get('cut_boundary')
                    acc.cut_percentage = cut_percentage
                    acc.prepaid = prepaid
                    acc.cut_bouldery = cut_boundary
                acc.save()

                context={'message':'Successfuly Edited shop '+acc.name}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('agent_index')
    
    return redirect('index')


@login_required
def super_admin_view(request):
    if request.user.is_superuser:
        return render(request,'agent/super_agent.html')
    return redirect('index')


@csrf_exempt
@login_required
def add_agent(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            try:
                name = request.GET['name']
                user_name = request.GET['user_name']
                password = request.GET['password']
                phone_number = request.GET['phone_number']
                percentage = request.GET['percentage']
                prepaid = request.GET.get('prepaid') == 'on'
                balance = request.GET.get('balance')

                user = User.objects.create_user(username=user_name, email=user_name+'@goldenbingos.com', password=password)
                user.save()

                acc = Agent.objects.create(
                    user=user,
                    name=name,
                    phone_number=phone_number,
                    account=Decimal(balance),
                    prepaid=prepaid,
                    percentage=Decimal(percentage),
                    backup_password=password,
                )
                acc.save()

                context={'message':'Successfuly added Agent '+acc.name}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('super_admin')
    
    return redirect('index')

@csrf_exempt
@login_required
def agent_activate_deactivate_view(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('user')
                user = User.objects.get(id=int(user_id))
                if user.is_active:
                    user.is_active = False
                else:
                    user.is_active = True

                user.save()

                context={'message':'Successfully changed Agent '}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('super_admin')
    
    return redirect('index')
            

@csrf_exempt
@login_required
def get_agent_info(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('user')
                user = User.objects.get(id=int(user_id))

                acc = Agent.objects.get(user=user)
                shop_stat = {}
                
                shop_stat['balance'] = round(float(acc.account),2)
                shop_stat['name'] = acc.name
                shop_stat['percentage'] = acc.percentage
                if acc.prepaid:
                    shop_stat['prepaid'] = 'checked'
                else:
                    shop_stat['prepaid'] = ''
                shop_stat['phone_number'] = acc.phone_number
                shop_stat['user_name'] = user.username
                shop_stat['password'] = acc.backup_password

                return JsonResponse(shop_stat)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('super_admin')
    
    return redirect('index')

@csrf_exempt
@login_required
def agent_add_balance(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            try:
                user_id = request.GET.get('id')
                user = User.objects.get(id=int(user_id))
                acc = Agent.objects.get(user=user)
                balance = request.GET.get('account')
                acc.account += Decimal(balance)
                acc.save()
                context={'message':'Successfully added balance to Agent '}
                return JsonResponse(context)
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('super_admin')
    
    return redirect('index')

@csrf_exempt
@login_required
def edit_agent(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            try:
                user_id = request.GET['id']
                name = request.GET['name']
                user_name = request.GET['user_name']
                password = request.GET['password']
                phone_number = request.GET['phone_number']
                percentage = request.GET['percentage']
                balance = request.GET['balance']
                prepaid = request.GET.get('prepaid') == 'on'

                user = User.objects.get(id=int(user_id))
                user.username = user_name
                user.set_password(password)
                user.save()

                acc = Agent.objects.get(user=user)
                acc.name=name
                acc.backup_password = password
                acc.phone_number = phone_number
                acc.percentage = percentage
                acc.account = Decimal(balance)
                acc.prepaid = prepaid
                acc.save()

                context={'message':'Successfuly Edited Agent '+acc.name}
                return JsonResponse(context)
            
            except ValueError:
                context={'message':'Error has Happened'}
                return JsonResponse(context)
        
        return redirect('super_admin')
    
    return redirect('index')


@csrf_exempt
@login_required
def view_agent_view(request,id):
    if request.user.is_superuser:
        try:
            user = User.objects.get(id=int(id))

            acc = Agent.objects.get(user=user)
            return render(request,'agent/agent_stat.html',{'agent':acc})
        except ValueError:
            return redirect('super_admin')
            
    return redirect('super_admin')
    
