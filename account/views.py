from datetime import datetime, timedelta, time
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from account.models import Account, Profile, UserGameCounter
from agent.models import Agent, AgentAccount
from cashier.models import Cashier
from game.models import CashierGame, UserGame
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists in the database
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                acc = Account.objects.get(user=user)
                if acc.agent and acc.agent.id == 3:
                    error_message = "Your account is inactive. Please call 0944 42 42 52."
                else:
                    error_message = "Your account is inactive. Please call 0911 95 99 68."
            else:
                # Authenticate the user only if they are active
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_superuser:  # Check if the user is an admin (staff member)
                        login(request, user)
                        return redirect('super_admin')  # Redirect to the owner's dashboard

                    else:
                        login(request, user)
                        try:
                            agent = Agent.objects.get(user=user)
                            if agent is not None:
                                return redirect('agent_index')
                            else:
                                return redirect('index')
                        except Agent.DoesNotExist:
                            try:
                                cashier = Cashier.objects.get(user=user)
                                if cashier is not None:
                                    return redirect('cashier')
                                else:
                                    return redirect('index')
                            except Cashier.DoesNotExist:
                                return redirect('index')  # Redirect to the user's dashboard
                else:
                    error_message = "Invalid username or password."
        except User.DoesNotExist:
            error_message = "Invalid username or password."
    else:
        error_message = "Enter username and password"

    return render(request, 'account/login.html', {'error': error_message})



def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    today = datetime.now().date()
    today_earning = 0
    admin_cut = 0
    game_counter = 0

    # Safely get user account
    acc = Account.objects.filter(user=user).first()
    if not acc:
        return render(request, 'account/dashboard.html', {
            'error': "No account found for this user."
        })

    today_game_counter = UserGameCounter.objects.filter(user=user).first()
    if not today_game_counter:
        today_game_counter = UserGameCounter.objects.create(user=user, game_counter=0)

    # Safely handle agent accounts
    agent_accounts_data = []
    if acc.agent:
        agent_accounts = AgentAccount.objects.filter(
            agent=acc.agent,
            is_active=True
        ).order_by('payment_method')

        agent_accounts_data = [
            {
                'id': agent_acc.id,
                'account_number': agent_acc.account_number,
                'payment_method_label': agent_acc.get_payment_method_display(),
                'account_owner_name': agent_acc.account_owner_name,
            }
            for agent_acc in agent_accounts
        ]

    if request.POST:
        selected_date = request.POST.get('datefilter')
        if selected_date:
            start_date_str, end_date_str = selected_date.split(' - ')
            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date = datetime.strptime(end_date_str, '%m/%d/%Y') + timedelta(days=1) - timedelta(seconds=1)

            cashiers = Cashier.objects.filter(shop=acc)
            is_cashier = cashiers.count() > 1
            game_data, cashier_data = [], []
            cashier_stat = {c.name: 0 for c in cashiers}

            latest_user_games = UserGame.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).order_by('-created_at')

            for game in latest_user_games:
                today_earning += game.game.shop_cut
                game_counter += 1
                admin_cut += game.game.admin_cut

                if is_cashier:
                    cashier_data = []
                    for cashier in cashiers:
                        cashier_game = CashierGame.objects.filter(user=cashier.user, game=game.game).first()
                        if cashier_game:
                            cashier_data.append({
                                'name': cashier.name,
                                'collected': cashier_game.collected,
                                'paid': cashier_game.pied,
                            })
                            cashier_stat[cashier.name] += cashier_game.collected - cashier_game.pied

                    game_data.append({'cashier_data': cashier_data, 'game': game.game})

            cashier_stat_list = [{'name': c.name, 'earning': cashier_stat[c.name]} for c in cashiers] if is_cashier else []

            context = {
                'acc': acc,
                'counter': game_counter,
                'letest_games': latest_user_games,
                'today_earning': today_earning,
                'admin_cut': admin_cut,
                'filter': True,
                'cashier': is_cashier,
                'game_data': game_data,
                'cashier_stat': cashiers,
                'cashier_earning': cashier_stat_list,
                'agents_accounts': agent_accounts_data,
            }

            return render(request, 'account/dashboard.html', context)

    # Default (non-filtered) data
    latest_user_games = UserGame.objects.filter(user=user).order_by('-created_at')[:100]
    start_of_day = datetime.combine(today, time(4, 0, 0))
    end_of_day = datetime.combine(today + timedelta(days=1), time(3, 59, 59))

    cashiers = Cashier.objects.filter(shop=acc)
    is_cashier = cashiers.count() > 1
    game_data, cashier_data = [], []
    cashier_stat = {c.name: 0 for c in cashiers}

    user_games = UserGame.objects.filter(user=user, created_at__range=(start_of_day, end_of_day)).order_by('-created_at')

    for game in user_games:
        today_earning += game.game.shop_cut
        if is_cashier:
            cashier_data = []
            for cashier in cashiers:
                cashier_game = CashierGame.objects.filter(user=cashier.user, game=game.game).first()
                if cashier_game:
                    cashier_data.append({
                        'name': cashier.name,
                        'collected': cashier_game.collected,
                        'paid': cashier_game.pied,
                    })
                    cashier_stat[cashier.name] += cashier_game.collected - cashier_game.pied

            game_data.append({'cashier_data': cashier_data, 'game': game.game})

    cashier_stat_list = [{'name': c.name, 'earning': cashier_stat[c.name]} for c in cashiers] if is_cashier else []

    context = {
        'acc': acc,
        'counter': today_game_counter.game_counter,
        'letest_games': latest_user_games,
        'today_earning': today_earning,
        'cashier': is_cashier,
        'game_data': game_data[:100],
        'cashier_stat': cashiers,
        'cashier_earning': cashier_stat_list,
        'agents_accounts': agent_accounts_data,
    }
    return render(request, 'account/dashboard.html', context)

@login_required
def setting_view(request):
    user = request.user
    today_game_counter = UserGameCounter.objects.get(user=user)
    acc = Account.objects.get(user=user)
    return render(request,'account/setting.html',{"acc":acc,"cout":today_game_counter})


@login_required
def setting_view(request):
    user = request.user
    today_game_counter = UserGameCounter.objects.get(user=user)
    acc = Account.objects.get(user=user)
    return render(request,'account/setting.html',{"acc":acc,"cout":today_game_counter})


@login_required
def update_settings(request):
    user = request.user  # Get the authenticated user
    data = json.loads(request.body)  # Parse JSON data
    display_info = data.get("display_info", True)
    jackpot_percent = data.get("jackpot_percent", 0.00)
    jackpot_amount = data.get("jackpot_amount", 0.00)
    acc = Account.objects.get(user=user)
    if acc:
        acc.jackpot_percent = jackpot_percent
        acc.jackpot_amount = jackpot_amount
        acc.save()
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    profile.display_info = display_info
    profile.save()

    return JsonResponse({"success": True, "message": "Settings saved successfully!"})