from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from account.models import Account, UserGameCounter
from agent.models import Agent
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
    today_game_counter = UserGameCounter.objects.get(user=user)
    acc = Account.objects.get(user=user)
    if request.POST:
        selected_date = request.POST.get('datefilter')
        if selected_date:
            start_date_str, end_date_str = selected_date.split(' - ')
            # Convert the date strings to datetime objects
            # Convert to naive datetime first
            start_date_naive = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date_naive = datetime.strptime(end_date_str, '%m/%d/%Y')
            
            # Make them timezone-aware using the current timezone
            start_date = timezone.make_aware(start_date_naive, timezone.get_current_timezone()) + timedelta(hours=4)
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone()) + timedelta(days=1, hours=3, minutes=59, seconds=59)
            cashiers = Cashier.objects.filter(shop=acc)
            is_cashier = False
            game_data = []
            cashier_data=[]
            cashier_stat = {}
            if cashiers.count() > 1:
                is_cashier = True
                for cashier in cashiers:
                    cashier_stat[cashier.name] = 0
            latest_user_games = UserGame.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).order_by('-created_at')
            all_user_games = UserGame.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).order_by('-created_at')
            for game in all_user_games:
                today_earning += game.game.shop_cut
                game_counter+= 1
                admin_cut+= game.game.admin_cut
                
                if is_cashier:
                    cashier_data = []
                    for cashier in cashiers:
                        cashier_game = CashierGame.objects.get(user=cashier.user,game=game.game)
                        cashier_data.append({
                            'name': cashier.name,
                            'collected': cashier_game.collected,
                            'paid': cashier_game.pied,
                        })
                        cashier_stat[cashier.name] += cashier_game.collected - cashier_game.pied
                    game_data.append({
                        'cashier_data': cashier_data,
                        'game': game.game
                    })
            cashier_stat_list = []
            
            if is_cashier:
                cashier_stat_list = [{'name': cashier.name, 'earning': cashier_stat[cashier.name]} for cashier in cashiers]

            context={'acc':acc,'counter':game_counter,'letest_games':latest_user_games,'today_earning':today_earning,'admin_cut':admin_cut,'filter':True,'cashier':is_cashier,'game_data':game_data,'cashier_stat':cashiers,'cashier_earning':cashier_stat_list}
            
            return render(request,'account/dashboard.html',context)

    latest_user_games = UserGame.objects.filter(user=user).order_by('-created_at')[:100]
    start_of_day = datetime.combine(today, time(4, 0, 0))  # 4:00 AM today
    end_of_day = datetime.combine(today + timedelta(days=1), time(3, 59, 59))  # 3:59:59 AM next daycashiers = Cashier.objects.filter(shop=acc)
    is_cashier = False
    game_data = []
    cashier_data= []
    cashier_stat = {}
    if cashiers.count() > 1:
        is_cashier = True
        for cashier in cashiers:
            cashier_stat[cashier.name] = 0
    user_games = UserGame.objects.filter(
        user=user,
        created_at__range=(start_of_day, end_of_day)
    ).order_by('-created_at')

    cashier_stat_list = []

    for game in user_games:
        today_earning += game.game.shop_cut
        if is_cashier:
            cashier_data = []
            for cashier in cashiers:
                cashier_game = CashierGame.objects.get(user=cashier.user,game=game.game)
                cashier_data.append({
                    'name': cashier.name,
                    'collected': cashier_game.collected,
                    'paid': cashier_game.pied,
                })
                cashier_stat[cashier.name] += cashier_game.collected - cashier_game.pied
            game_data.append({
                'cashier_data': cashier_data,
                'game': game.game
            })
    if is_cashier:
        cashier_stat_list = [{'name': cashier.name, 'earning': cashier_stat[cashier.name]} for cashier in cashiers]

    context={'acc':acc,'counter':today_game_counter.game_counter,'letest_games':latest_user_games,'today_earning':today_earning,'cashier':is_cashier,'game_data':game_data[:100],'cashier_stat':cashiers,'cashier_earning':cashier_stat_list}
    return render(request,'account/dashboard.html',context)


@login_required
def setting_view(request):
    user = request.user
    today_game_counter = UserGameCounter.objects.get(user=user)
    acc = Account.objects.get(user=user)
    return render(request,'account/setting.html',{"acc":acc,"cout":today_game_counter})
