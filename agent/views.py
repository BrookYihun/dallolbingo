from datetime import datetime, timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import connection, models
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

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

    # Get the agent
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, account, name, privilege, min_stake 
            FROM agent_agent 
            WHERE user_id = %s
        """, [request.user.id])
        agent = cursor.fetchone()

    if not agent:
        return JsonResponse({'message': 'ERROR'})

    agent_id, agent_account, agent_name, agent_privilege, agent_min_stake = agent
    
    # Get all shop statistics in one optimized query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                a.id, a.user_id, a.name, a.account, a.percentage, a.prepaid, a.cut_percentage, a.cut_bouldery, a.total_earning,
                ugc.game_counter, ugc.last_game_date,
                (SELECT COUNT(*) FROM game_usergame WHERE user_id = a.user_id) AS total_games_played,
                (SELECT SUM(gg.shop_cut) FROM game_usergame ug 
                 JOIN game_game gg ON ug.game_id = gg.id 
                 WHERE ug.user_id = a.user_id AND DATE(gg.created_at) = %s) AS today_earning,
                (SELECT SUM(gg.shop_cut - gg.admin_cut) FROM game_usergame ug 
                 JOIN game_game gg ON ug.game_id = gg.id 
                 WHERE ug.user_id = a.user_id AND DATE(gg.created_at) = %s) AS net_today,
                au.is_active
            FROM account_account a
            LEFT JOIN account_usergamecounter ugc ON a.user_id = ugc.user_id
            LEFT JOIN auth_user au ON a.user_id = au.id
            WHERE a.agent_id = %s
        """, [today, today, agent_id])

        shops_stat = []
        total_agent_earning = 0
        today_agent_earning = 0

        for shop in cursor.fetchall():
            (shop_id, user_id, shop_name, account, percentage, prepaid, cut_percentage, cut_bouldery, total_earning,
             game_counter, last_game_date, total_games_played, today_earning, net_today, is_active) = shop

            total_games_played_today = game_counter if last_game_date == today else 0

            shop_stat = {
                'account': round(float(account), 2),
                'total_games_played_today': total_games_played_today,
                'total_games_played': total_games_played or 0,
                'name': shop_name,
                'id': user_id,
                'percentage': percentage,
                'prepaid': prepaid,
                'cut_percentage': cut_percentage,
                'cut_boundary': cut_bouldery,
                'active': 'Deactivate' if is_active else 'Activate',
                'today_earning': round(today_earning or 0, 2),
                'total_earning': round(float(total_earning or 0), 2),
            }

            today_agent_earning += today_earning or 0
            total_agent_earning += float(total_earning or 0)
            shops_stat.append(shop_stat)

    agent_data = {
        'account': agent_account,
        'name': agent_name,
        'privilege': agent_privilege,
        'min_stake': agent_min_stake,
    }

    context = {
        'shops_stat': shops_stat,
        'agent': agent_data,
        'num_shops': len(shops_stat),
        'total_earning': round(total_agent_earning, 2),
        'today_earning': round(today_agent_earning, 2),
    }

    return JsonResponse(context)

@login_required
def admin_get_shop_stat(request, id):
    today = timezone.now().date()

    # Get the agent
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, account, name, privilege, min_stake 
            FROM agent_agent 
            WHERE user_id = %s
        """, [id])
        agent = cursor.fetchone()

    if not agent:
        return JsonResponse({'message': 'ERROR'})

    agent_id, agent_account, agent_name, agent_privilege, agent_min_stake = agent

    # Get all shops under the agent
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, user_id, name, account, percentage, prepaid, cut_percentage, cut_bouldery, total_earning 
            FROM account_account 
            WHERE agent_id = %s
        """, [agent_id])
        shops = cursor.fetchall()

    if not shops:
        return JsonResponse({'message': 'No shops found'})

    shop_ids = tuple(shop[1] for shop in shops)  # Extract user_ids from shops and convert to tuple

    if not shop_ids:  # Avoid SQL error if no shops exist
        return JsonResponse({'message': 'No shops found'})

    # Get game counters in bulk
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT user_id, game_counter, last_game_date FROM account_usergamecounter 
            WHERE user_id IN {shop_ids}
        """)
        game_counters = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    # Get total games played in bulk
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT user_id, COUNT(*) FROM game_usergame 
            WHERE user_id IN {shop_ids} GROUP BY user_id
        """)
        total_games_played = {row[0]: row[1] for row in cursor.fetchall()}

    # Get today's earnings in bulk
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT game_usergame.user_id, 
                   SUM(game_game.shop_cut) AS today_earning, 
                   SUM(game_game.shop_cut - game_game.admin_cut) AS net_today 
            FROM game_usergame 
            JOIN game_game ON game_usergame.game_id = game_game.id 
            WHERE game_usergame.user_id IN {shop_ids} AND DATE(game_game.created_at) = %s
            GROUP BY game_usergame.user_id
        """, [today])
        today_earnings = {row[0]: (float(row[1] or 0), float(row[2] or 0)) for row in cursor.fetchall()}

    # Get user active status in bulk
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, is_active FROM auth_user WHERE id IN {shop_ids}")
        user_status = {row[0]: row[1] for row in cursor.fetchall()}

    shops_stat = []
    total_agent_earning = 0
    today_agent_earning = 0

    for shop in shops:
        shop_id, user_id, shop_name, account, percentage, prepaid, cut_percentage, cut_bouldery, total_earning = shop

        # Extract values using dictionaries
        total_games_today = game_counters.get(user_id, (0, None))
        total_games_played_today = total_games_today[0] if total_games_today[1] == today else 0
        total_games_played_count = total_games_played.get(user_id, 0)
        today_earning, net_today = today_earnings.get(user_id, (0, 0))
        is_active = user_status.get(user_id, False)

        shop_stat = {
            'account': round(float(account), 2),
            'total_games_played_today': total_games_played_today,
            'total_games_played': total_games_played_count,
            'name': shop_name,
            'id': user_id,
            'percentage': percentage,
            'prepaid': prepaid,
            'cut_percentage': cut_percentage,
            'cut_boundary': cut_bouldery,
            'active': 'Deactivate' if is_active else 'Activate',
            'today_earning': round(today_earning, 2),
            'total_earning': round(float(total_earning), 2),
        }

        today_agent_earning += today_earning
        total_agent_earning += float(total_earning)
        shops_stat.append(shop_stat)

    agent_data = {
        'account': agent_account,
        'name': agent_name,
        'privilege': agent_privilege,
        'min_stake': agent_min_stake,
    }

    context = {
        'shops_stat': shops_stat,
        'agent': agent_data,
        'num_shops': len(shops),
        'total_earning': round(total_agent_earning, 2),
        'today_earning': round(today_agent_earning, 2),
    }

    return JsonResponse(context)

@login_required
def get_agent_stat(request):
    today = now().date()

    if request.user.is_superuser:
        # Get all agents
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, name, percentage, prepaid, privilege, account 
                FROM agent_agent
            """)
            agents = cursor.fetchall()

        if not agents:
            return JsonResponse({'message': 'No agents found'})

        agent_ids = [agent[0] for agent in agents]
        agent_users = {agent[1]: agent for agent in agents}

    with connection.cursor() as cursor:
        if agent_ids:  # Ensure agent_ids is not empty
            query = """
                SELECT id, user_id, agent_id, total_earning, percentage, account 
                FROM account_account 
                WHERE agent_id = ANY(%s)
            """
            cursor.execute(query, (list(agent_ids),))  # Convert to list for ANY()
        else:
            cursor.execute("""
                SELECT id, user_id, agent_id, total_earning, percentage, account 
                FROM account_account 
                WHERE 1=0
            """)  # Return empty result if agent_ids is empty

        shops = cursor.fetchall()

        if not shops:
            return JsonResponse({'message': 'No shops found'})

        shop_user_ids = [shop[1] for shop in shops]
        shop_agent_map = {shop[1]: shop for shop in shops}

        # Get game counters
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, game_counter, last_game_date 
                FROM account_usergamecounter 
                WHERE user_id = ANY(%s)
            """, (list(shop_user_ids),))
            game_counters = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        # Get today's earnings for all shops
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT game_usergame.user_id, SUM(game_game.admin_cut) 
                FROM game_usergame 
                JOIN game_game ON game_usergame.game_id = game_game.id 
                WHERE game_usergame.user_id = ANY(%s) AND DATE(game_game.created_at) = %s
                GROUP BY game_usergame.user_id
            """, [list(agent_ids), today])  # Remove the extra tuple around list(agent_ids)

            today_earnings = {row[0]: float(row[1]) for row in cursor.fetchall()}

        # Get total earnings per agent
        agent_earnings = {agent_id: 0 for agent_id in agent_ids}
        today_agent_earnings = {agent_id: 0 for agent_id in agent_ids}
        today_agent_games = {agent_id: 0 for agent_id in agent_ids}

        for shop in shops:
            shop_id, user_id, agent_id, total_earning, percentage, account = shop
            game_counter = game_counters.get(user_id, (0, None))
            today_games = game_counter[0] if game_counter[1] == today else 0
            today_earning = today_earnings.get(user_id, 0)

            agent_earnings[agent_id] += total_earning * percentage
            today_agent_earnings[agent_id] += today_earning
            today_agent_games[agent_id] += today_games

        # Build agent statistics
        agents_stat = []
        total_shops = len(shops)
        total_earning = sum(agent_earnings.values())
        today_earning = sum(today_agent_earnings.values())

        for agent in agents:
            agent_id, user_id, name, percentage, prepaid, privilege, account = agent
            agents_stat.append({
                'name': name,
                'percentage': percentage,
                'prepaid': prepaid,
                'privilege': privilege,
                'id': user_id,
                'account': account,
                'total_shops': sum(1 for shop in shops if shop[2] == agent_id),
                'total_earning': round(agent_earnings[agent_id], 2),
                'total_net': round(agent_earnings[agent_id] - (agent_earnings[agent_id] * percentage), 2),
                'today_game': today_agent_games[agent_id],
                'today_earning': round(today_agent_earnings[agent_id], 2),
                'active': 'Deactivate' if agent_users[user_id][1] else 'Activate'
            })

        context = {
            'agents_stat': agents_stat,
            'num_shops': total_shops,
            'num_agent': len(agents),
            'total_earning': round(total_earning, 2),
            'today_earning': round(today_earning, 2)
        }
        return JsonResponse(context)

    # If not superuser, fetch stats for the logged-in agent
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, user_id, name, privilege, min_stake, account 
            FROM agent_agent 
            WHERE user_id = %s
        """, [request.user.id])
        agent = cursor.fetchone()

    if not agent:
        return JsonResponse({'message': 'ERROR'})

    agent_id, user_id, name, privilege, min_stake, account = agent

    # Fetch all shops under the agent
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, user_id, name, percentage, cut_percentage, cut_bouldery, prepaid, total_earning, account 
            FROM account_account 
            WHERE agent_id = %s
        """, [agent_id])
        shops = cursor.fetchall()

    if not shops:
        return JsonResponse({'message': 'No shops found'})

    shop_user_ids = [shop[1] for shop in shops]

    # Fetch game counters for shops
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, game_counter, last_game_date 
            FROM account_usergamecounter 
            WHERE user_id IN %s
        """, [tuple(shop_user_ids)])
        game_counters = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    # Fetch today's earnings for shops
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT game_usergame.user_id, SUM(game_game.shop_cut), SUM(game_game.shop_cut - game_game.admin_cut) 
            FROM game_usergame 
            JOIN game_game ON game_usergame.game_id = game_game.id 
            WHERE game_usergame.user_id IN %s AND DATE(game_game.created_at) = %s
            GROUP BY game_usergame.user_id
        """, [tuple(shop_user_ids), today])
        today_earnings = {row[0]: (float(row[1]), float(row[2])) for row in cursor.fetchall()}

    # Get user active status
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, is_active FROM auth_user WHERE id IN %s
        """, [tuple(shop_user_ids)])
        user_status = {row[0]: row[1] for row in cursor.fetchall()}

    # Build shop statistics
    shops_stat = []
    total_agent_earning = 0
    today_agent_earning = 0

    for shop in shops:
        shop_id, user_id, name, percentage, cut_percentage, cut_bouldery, prepaid, total_earning, account = shop
        game_counter = game_counters.get(user_id, (0, None))
        total_games_played_today = game_counter[0] if game_counter[1] == today else 0
        today_earning, net_today = today_earnings.get(user_id, (0, 0))
        is_active = user_status.get(user_id, False)

        shops_stat.append({
            'account': round(float(account), 2),
            'total_games_played_today': total_games_played_today,
            'total_games_played': game_counter[0],
            'name': name,
            'id': user_id,
            'percentage': percentage,
            'cut_percentage': cut_percentage,
            'cut_boundary': cut_bouldery,
            'prepaid': prepaid,
            'active': 'Deactivate' if is_active else 'Activate',
            'today_earning': round(today_earning, 2),
            'total_earning': round(float(total_earning), 2)
        })

        today_agent_earning += today_earning
        total_agent_earning += float(total_earning)

    agent_data = {
        'account': account,
        'name': name,
        'privilege': privilege,
        'min_stake': min_stake
    }

    context = {
        'shops_stat': shops_stat,
        'agent': agent_data,
        'num_shops': len(shops),
        'total_earning': round(total_agent_earning, 2),
        'today_earning': round(today_agent_earning, 2)
    }
    return JsonResponse(context)

@login_required
def get_shop_stat_filter(request):
    today = timezone.now().date()
    selected_date = request.GET.get('datefilter', None)

    with connection.cursor() as cursor:
        # Get the agent info
        cursor.execute("""
            SELECT id, account, name, privilege, min_stake 
            FROM agent_agent 
            WHERE user_id = %s
        """, [request.user.id])
        agent = cursor.fetchone()

        if not agent:
            return JsonResponse({'message': 'Agent not found'}, status=404)

        agent_id, agent_account, agent_name, agent_privilege, agent_min_stake = agent

        # Get all shops under the agent
        cursor.execute("""
            SELECT a.id, a.name, a.account, a.percentage, a.cut_percentage, 
                   a.cut_bouldery, a.prepaid, u.id as user_id, u.is_active
            FROM account_account a
            JOIN auth_user u ON a.user_id = u.id
            WHERE a.agent_id = %s
        """, [agent_id])
        shops = cursor.fetchall()

        shop_ids = [shop[7] for shop in shops]  # Extract user_ids

        if not shop_ids:
            return JsonResponse({
                'shops_stat': [],
                'agent': {
                    'account': agent_account,
                    'name': agent_name,
                    'privilege': agent_privilege,
                    'min_stake': agent_min_stake
                },
                'num_shops': 0,
                'total_earning': 0,
                'today_earning': 0
            })

        if selected_date:
            start_date_str, end_date_str = selected_date.split(' - ')
            
            # Convert to naive datetime first
            start_date_naive = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date_naive = datetime.strptime(end_date_str, '%m/%d/%Y')
            
            # Make them timezone-aware using the current timezone
            start_date = timezone.make_aware(start_date_naive, timezone.get_current_timezone())
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone()) + timedelta(days=1) - timedelta(seconds=1)

        else:
            start_date = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

        # Fetch game statistics for shops with proper timestamptz handling
        cursor.execute("""
            SELECT ug.user_id, 
                   COUNT(ug.id) AS total_games_played, 
                   COALESCE(SUM(CASE WHEN g.created_at >= %s AND g.created_at < %s THEN g.shop_cut END), 0) AS today_earning,
                   COALESCE(SUM(g.shop_cut), 0) AS total_earning
            FROM game_usergame ug
            JOIN game_game g ON ug.game_id = g.id
            WHERE ug.user_id = ANY(%s)
            GROUP BY ug.user_id
        """, [start_date, end_date, list(shop_ids)])

        game_stats = {stat[0]: stat[1:] for stat in cursor.fetchall()}

        # Fetch today's game counters
        cursor.execute("""
            SELECT user_id, game_counter 
            FROM account_usergamecounter 
            WHERE user_id = ANY(%s) 
            AND last_game_date = %s::timestamptz
        """, [list(shop_ids), today])
        game_counters = {row[0]: row[1] for row in cursor.fetchall()}

    # Prepare response
    shops_stat = []
    total_agent_earning = 0
    today_agent_earning = 0

    for shop in shops:
        user_id = shop[7]
        stat = game_stats.get(user_id, (0, 0, 0))

        shop_stat = {
            'id': user_id,
            'name': shop[1],
            'account': round(float(shop[2]), 2),
            'total_games_played_today': game_counters.get(user_id, 0),
            'total_games_played': stat[0],
            'percentage': shop[3],
            'cut_percentage': shop[4],
            'cut_boundary': shop[5],
            'prepaid': shop[6],
            'total_earning': round(stat[2], 2),
            'today_earning': round(stat[1], 2),
            'active': 'Deactivate' if shop[8] else 'Activate'
        }

        total_agent_earning += shop_stat['total_earning']
        today_agent_earning += shop_stat['today_earning']

        shops_stat.append(shop_stat)

    context = {
        'shops_stat': shops_stat,
        'agent': {
            'account': agent_account,
            'name': agent_name,
            'privilege': agent_privilege,
            'min_stake': agent_min_stake
        },
        'num_shops': len(shops),
        'total_earning': round(total_agent_earning, 2),
        'today_earning': round(today_agent_earning, 2)
    }

    return JsonResponse(context)


@login_required
def admin_get_shop_stat_filter(request, id):
    today = timezone.now().date()
    selected_date = request.GET.get('datefilter', None)
    user = get_object_or_404(User, id=int(id))
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, account, name, privilege, min_stake 
            FROM agent_agent 
            WHERE user_id = %s
        """, [user.id])
        agent = cursor.fetchone()
        
        if not agent:
            return JsonResponse({'message': 'Agent not found'}, status=404)
        
        agent_id, agent_account, agent_name, agent_privilege, agent_min_stake = agent
        
        cursor.execute("""
            SELECT a.id, a.name, a.account, a.percentage, a.cut_percentage, 
                   a.cut_bouldery, a.prepaid, u.id as user_id, u.is_active
            FROM account_account a
            JOIN auth_user u ON a.user_id = u.id
            WHERE a.agent_id = %s
        """, [agent_id])
        shops = cursor.fetchall()
        
        shop_ids = [shop[7] for shop in shops]  # Extract user_ids
        
        if not shop_ids:
            return JsonResponse({
                'shops_stat': [],
                'agent': {
                    'account': agent_account,
                    'name': agent_name,
                    'privilege': agent_privilege,
                    'min_stake': agent_min_stake
                },
                'num_shops': 0,
                'total_earning': 0,
                'today_earning': 0
            })
        
        if selected_date:
            start_date_str, end_date_str = selected_date.split(' - ')
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%m/%d/%Y'))
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%m/%d/%Y')) + timedelta(days=1) - timedelta(seconds=1)
        else:
            start_date = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
        
        cursor.execute("""
            SELECT ug.user_id, COUNT(ug.id) AS total_games_played, 
                   COALESCE(SUM(CASE WHEN g.created_at >= %s AND g.created_at <= %s THEN g.shop_cut END), 0) AS today_earning,
                   COALESCE(SUM(g.shop_cut), 0) AS total_earning
            FROM game_usergame ug
            JOIN game_game g ON ug.game_id = g.id
            WHERE ug.user_id = ANY(%s)
            GROUP BY ug.user_id
        """, [start_date, end_date, list(shop_ids)])
        
        game_stats = {stat[0]: stat[1:] for stat in cursor.fetchall()}
        
        cursor.execute("""
            SELECT user_id, game_counter 
            FROM account_usergamecounter 
            WHERE user_id = ANY(%s) 
            AND last_game_date = %s
        """, [list(shop_ids), today])
        game_counters = {row[0]: row[1] for row in cursor.fetchall()}
    
    shops_stat = []
    total_agent_earning = 0
    today_agent_earning = 0
    
    for shop in shops:
        user_id = shop[7]
        stat = game_stats.get(user_id, (0, 0, 0))
        shop_stat = {
            'id': user_id,
            'name': shop[1],
            'account': round(float(shop[2]), 2),
            'total_games_played_today': game_counters.get(user_id, 0),
            'total_games_played': stat[0],
            'percentage': shop[3],
            'cut_percentage': shop[4],
            'cut_boundary': shop[5],
            'prepaid': shop[6],
            'total_earning': round(stat[2], 2),
            'today_earning': round(stat[1], 2),
            'active': 'Deactivate' if shop[8] else 'Activate'
        }
        total_agent_earning += stat[2]
        today_agent_earning += stat[1]
        shops_stat.append(shop_stat)
    
    agent_data = {
        'account': agent_account,
        'name': agent_name,
        'privilege': agent_privilege,
        'min_stake': agent_min_stake
    }
    
    context = {
        'shops_stat': shops_stat,
        'agent': agent_data,
        'num_shops': len(shops),
        'total_earning': round(total_agent_earning, 2),
        'today_earning': round(today_agent_earning, 2)
    }
    
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
    
