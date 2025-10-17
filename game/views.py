import random
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from account.models import Account, UserGameCounter
from agent.models import Agent
from cashier.models import Cashier
from game.models import Card, CashierGame, Game, UserGame
from django.contrib.auth.models import User

# Create your views here.
@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('super_admin')
    try:
        agent = Agent.objects.get(user=request.user)
        return redirect('agent_index')
    except Agent.DoesNotExist:
        pass
    numbers = range(1, 76)
    letters = ['B', 'I', 'N', 'G', 'O']
    numbers_per_row = 15
    bingo_rows = []
    for letter in letters:
        row_numbers = numbers[:numbers_per_row]
        numbers = numbers[numbers_per_row:]
        bingo_rows.append({'letter': letter, 'numbers': row_numbers})

    context = {'bingoRows': bingo_rows}
    return render(request,'game/index.html',context)

@csrf_exempt
@login_required
def new_game_view(request):
    if request.method == 'POST':
        try:
            user = request.user
            acc = Account.objects.get(user=user)

            if acc.prepaid and acc.account<0:
                return redirect('index')
            
            selected_numbers = request.POST.getlist('players')
            players_selected = [int(num) for num in selected_numbers]
            cut_per = acc.cut_percentage
            bonus = request.POST.get('bonus') == 'on'
            free = request.POST.get('free') == 'on'
            stake = request.POST.get('stake')
            stake = request.POST.get('stake')
            if not stake or not stake.isdigit():
                stake = 20  # Default stake if not provided or invalid
            game_id = int(request.POST.get('game'))
            game = Game.objects.get(id=game_id)
            game.stake = int(stake)
            game.played = 'PLAYING'
            game.bonus = bonus
            game.free = free
            game.save()
            user_games = UserGame.objects.filter(user=request.user)
            user_game_count = user_games.count()
            if not user_games.filter(game=game).exists():
                user_game = UserGame.objects.create(game=game, user=request.user, game_number=user_game_count + 1)
                user_game.save()
                user_game_counter = UserGameCounter.objects.get(user=request.user)
                user_game_counter.increment_game_counter()
                user_game_counter.save()
            time = datetime.now()
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            players = []
            if game.playerCard:
                players = json.loads(game.playerCard)
            cashiers = Cashier.objects.filter(shop=acc)
            if cashiers.count() > 1:
                selected_players = []

                for cashier in cashiers:
                    cashier_game = get_object_or_404(CashierGame, user=cashier.user, game_id=game_id)
                    if cashier_game:
                        card_numbers = [int(card) for card in cashier_game.get_card_numbers()]
                        selected_players.extend(card_numbers)
                        cashier_game.collected = float(len(cashier_game.get_card_numbers())) * float(stake)
                        cashier.increment_balance(cashier_game.collected)
                        cashier.save()
                        cashier_game.save()


                for player in selected_players:
                    if player not in [player_card['card'] for player_card in players]:
                        new_player = {'time': formatted_time, 'card': player}
                        players.append(new_player)
                        game.numberofplayers = game.numberofplayers + 1
                
                paid = False
                winner = float(game.stake) * float(game.numberofplayers)
                if winner > acc.cut_bouldery:
                    winner = winner - (winner * float(cut_per))
                for cashier in cashiers:
                    cashier_game = get_object_or_404(CashierGame, user=cashier.user, game_id=game_id)
                    if cashier_game:
                        if cashier.balance > winner:
                            paid = True
                            cashier.decrement_balance(winner)
                            cashier_game.pied = winner
                            cashier_game.save()
                            break
                
                if not paid:
                    for cashier in cashiers:
                        cashier_game = get_object_or_404(CashierGame, user=cashier.user, game_id=game_id)
                        if cashier_game:
                            if cashier.balance <= winner:
                                winner -= float(cashier.balance)
                                cashier_game.pied = cashier.balance
                                cashier.decrement_balance(cashier.balance)
                                cashier_game.save()
                            elif cashier.balance > winner:
                                cashier.decrement_balance(winner)
                                cashier_game.pied = winner
                                cashier_game.save()
                                winner = 0
                                break

            else:
                for player in players_selected:
                    if player not in [player_card['card'] for player_card in players]:
                        new_player = {'time': formatted_time, 'card': player}
                        players.append(new_player)
                        game.numberofplayers = game.numberofplayers + 1

            game.playerCard = json.dumps(players)
            winner = float(game.stake) * float(game.numberofplayers)
            if winner > acc.cut_bouldery:
                game.shop_cut = float(winner) * float(cut_per)
                game.winner_price =  winner - game.shop_cut
                game.admin_cut = (float(winner) * float(cut_per)) * float(acc.percentage)
                
                #ACKPOT: DEDUCT FROM WINNER PRICE & ADD TO POOL
                if acc.jackpot_percent>0 and acc.jackpot_amount>0:
                    original_winner_price=Decimal(str(game.winner_price))
                    jackpot_contribution= original_winner_price*(acc.jackpot_percent/Decimal('100'))

                    if jackpot_contribution>original_winner_price:
                        jackpot_contribution= original_winner_price

                    game.winner_price=float(original_winner_price-jackpot_contribution)
                    acc.jackpot_balance+=jackpot_contribution

            else:
                game.shop_cut = 0
                game.winner_price = winner
                game.admin_cut = 0

            if winner > acc.cut_bouldery:
                acc.account= float(acc.account) - float(game.admin_cut)
                acc.total_earning += Decimal(str(game.shop_cut))
                acc.net_earning = acc.net_earning + Decimal(str(game.shop_cut - game.admin_cut))
                acc.save()
            if game.free and game.numberofplayers >= 30:
                game.winner_price = float(game.winner_price) - float(game.stake)
            game.save()
            bingo_cards = Card.objects.exclude(id__in=[p['card'] for p in players])
            user_game_counter = UserGameCounter.objects.get(user=request.user)
            numbers = range(1, 76)
            letters = ['B', 'I', 'N', 'G', 'O']
            numbers_per_row = 15
            bingo_rows = []
            for letter in letters:
                row_numbers = numbers[:numbers_per_row]
                numbers = numbers[numbers_per_row:]
                bingo_rows.append({'letter': letter, 'numbers': row_numbers})
            context = {'bingo_cards': bingo_cards, 'game': game,'game_counter':user_game_counter, 'players': players,'bingoRows': bingo_rows}
            return render(request,'game/index.html',context)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print("Error in new_game_view:", traceback_str)  # Or use logging
            return HttpResponse(f"Internal Server Error:\n{traceback_str}", status=500)
    acc = Account.objects.get(user= request.user)
    game = Game.objects.create()
    today_game_counter = UserGameCounter.objects.get(user=request.user)
    game.stake = 20
    game.save()
    cashiers = Cashier.objects.filter(shop=acc)
    is_cashier = False
    if cashiers.count() > 1:
        is_cashier = True
        for cashier in cashiers:
            cashier_game = CashierGame.objects.create(user=cashier.user,game=game)
            cashier_game.save()
            
    return render(request, 'game/new_game.html',{'counter':today_game_counter,'acc':acc,'game':game.id,'cashier':is_cashier,'cashiers':cashiers})

@login_required
def game_stat(request):
    gameId = request.GET.get('game')
    try:
        acc = Account.objects.get(user=request.user)
        cashiers = Cashier.objects.filter(shop=acc)
        if cashiers is not None:
            selected_players = []
            main_selected_players = []
            
            for cashier in cashiers:
                cashier_game = get_object_or_404(CashierGame, user=cashier.user, game_id=gameId)
                cashier_main = request.user.username + "_main_cashier"
                if cashier_game and cashier.user.username != cashier_main:
                    selected_players.extend(cashier_game.get_card_numbers())
                else:
                    main_selected_players.extend(cashier_game.get_card_numbers())
            
            cashier_game = CashierGame.objects.filter(game_id =gameId)
            cashier_stat_list = [{'name': cashier.user.username, 'selected_players': cashier.get_card_numbers()} for cashier in cashier_game if cashier.user.username != cashier_main]

            
            context = {'selected_players':cashier_stat_list,'main_selected':main_selected_players}
            return JsonResponse(context)
        context = {'message': 'None'}
        return JsonResponse(context)
    except Exception as e:
        print(e)  # Log the exception (optional)
        context = {'message': 'None'}
        return JsonResponse(context)
    
@login_required
def remove_player(request):
    card_id = request.GET.get('card')
    gameId = request.GET.get('game')
    user = request.user
    try:
        cashier_user = User.objects.get(username=user.username+"_main_cashier")
        # Retrieve the CashierGame object
        cashier_game = get_object_or_404(CashierGame, user=cashier_user, game_id=gameId)
        
        # Load the selected_players JSON
        selected_players = json.loads(cashier_game.selected_players)
        
        # Check if the player exists and remove it
        if card_id in selected_players:
            selected_players.remove(card_id)
            
            # Update the JSON field
            cashier_game.selected_players = json.dumps(selected_players)
            cashier_game.save()
            
            return JsonResponse({'status': 'success', 'message': 'Player removed successfully.'})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Player not found in selected_players.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def add_player(request):
    card_id = request.GET.get('card')
    gameId = request.GET.get('game')
    user = request.user
    try:
        cashier_user = User.objects.get(username=user.username+"_main_cashier")

        # Retrieve the CashierGame object
        cashier_game = get_object_or_404(CashierGame, user=cashier_user, game_id=gameId)
        
        # Load the selected_players JSON
        selected_players = json.loads(cashier_game.selected_players)
        
        # Check if the player does not exist and add it
        if card_id not in selected_players:
            selected_players.append(card_id)
            
            # Update the JSON field
            cashier_game.selected_players = json.dumps(selected_players)
            cashier_game.save()
            
            return JsonResponse({'status': 'success', 'message': 'Player added successfully.'})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Player already in selected_players.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@login_required
def update_stake(request):
    game_id = request.GET.get('game')
    stake = request.GET.get('stake')
    try:
        game = Game.objects.get(id=game_id)
        game.stake = int(stake)
        game.save()
        return JsonResponse({'status': 'success', 'message': 'Stake Updated.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def check_winner_view(request):
    card_id = request.GET.get('card')
    called_numbers_str = request.GET.get('called')
    patterns_str = request.GET.get('patterns',[])

    # Parse the string representation of the list into an actual list
    called_numbers = json.loads(called_numbers_str)
    gameId = request.GET.get('game')
    patterns = json.loads(patterns_str)
    if not called_numbers:
        context = {'called': called_numbers, 'message': 'No numbers called yet'}
        return JsonResponse(context)
    
    game = Game.objects.get(id=gameId)
    players = json.loads(game.playerCard)
    player_cards = [entry['card'] for entry in players]
    card_found = int(card_id) in player_cards
    game.total_calls = len(called_numbers)
    game.save()

    result = []
    if card_found:
        card = Card.objects.get(id=card_id)
        numbers = card.numbers
        winning_numbers,remaining_number = has_bingo(numbers, called_numbers,patterns)
        if len(winning_numbers)>0:

            if not remaining_number:
                winners = []
                if game.winners:
                    winners = json.loads(game.winners)
                if card.id not in winners:
                    # Append card.id if it is not in the list
                    winners.append(card.id)
                game.winners = json.dumps(winners)

            if game.bonus and not remaining_number:
                if len(called_numbers) == 4:
                    game.bonus_payed = 1
                elif len(called_numbers) == 5:
                    game.bonus_payed = 2
                elif len(called_numbers) == 6:
                    game.bonus_payed = 3
                elif len(called_numbers) == 7:
                    game.bonus_payed = 4
                elif len(called_numbers) == 8:
                    game.bonus_payed = 5
                elif len(called_numbers) == 9:
                    game.bonus_payed = 6
                elif len(called_numbers) == 10:
                    game.bonus_payed = 7
            
            if game.free and game.free_hit == 0 and game.numberofplayers >= 30:
                players = json.loads(game.playerCard)
                cards = [player_card['card'] for player_card in players]
                filtered_cards = [c for c in cards if c !=int(card_id) ]
                # game.shop_cut -= Decimal(game.stake)
                game.free_hit = random.choice(filtered_cards)
                cashierGame = CashierGame.objects.filter(game=game)
                # for cas in cashierGame:
                #     card_numbers = [int(card) for card in cas.get_card_numbers()]
                #     if int(game.free_hit) in card_numbers:
                #         cashier = Cashier.objects.get(user=cas.user)
                #         cas.collected -= Decimal(game.stake)
                #         cas.save()
                #         cashier.decrement_balance(game.stake)
                game.save()

            jackpot_won=False
            jackpot_payout=Decimal('0.00')

            try:
                shop_account=Account.objects.get(user=request.user)
                if shop_account.jackpot_balance >= shop_account.jackpot_amount > 0 and not remaining_number:
                    jackpot_won=True
                    jackpot_payout= shop_account.jackpot_amount
                    shop_account.jackpot_balance-= jackpot_payout
                    shop_account.save()
            except Account.DoesNotExist:
                pass

            result.append({'card_name': card.id, 'message': 'Bingo','free':game.free_hit, 'bonus':game.bonus_payed, 'winning_card': numbers, 'remaining_numbers': remaining_number,'called_numbers': called_numbers,'winning_numbers':winning_numbers,'card':numbers,'jackpot_won':jackpot_won,'jackpot_payout':float(jackpot_payout)})
            
        else:
            result.append({'card_name': card.id, 'message': 'No Bingo','card':numbers})
    else:
        result.append({'card_name': card_id, 'message': 'Not a Player'})

    game.save()
    context = {'called': called_numbers, 'result': result,'game':gameId}
    return JsonResponse(context)

from collections import OrderedDict

def has_bingo(card, called_numbers,patterns):

    called_numbers = list(OrderedDict.fromkeys(map(int, called_numbers)))

    called_numbers.append(0)  # Since we can't use add, we append 0 if it isn't already present
    if 0 not in called_numbers:
        called_numbers.append(0)
        
    if not patterns:
        patterns = ["1","2","3"]
    
    if isinstance(patterns, int):
        patterns = [str(patterns)]
    if isinstance(patterns, str):
        patterns = [patterns]
    
    winning_numbers = []
    
    if "2" in patterns:
        # Check diagonals
        diagonal2 = [card[i][i] for i in range(len(card))]
        diagonal1 = [card[i][len(card) - 1 - i] for i in range(len(card))]
        if all(number in called_numbers for number in diagonal2):
            winning_numbers.extend([1, 7, 13, 19, 25])
        if all(number in called_numbers for number in diagonal1):
            winning_numbers.extend([5, 9, 13, 17, 21])
            
    if "1" in patterns:
        # Check rows
        for row_index, row in enumerate(card):
            if all(number in called_numbers for number in row):
                winning_numbers.extend([(row_index * 5) + i for i in range(1, 6)])
    
        # Check columns
        for col in range(len(card[0])):
            if all(card[row][col] in called_numbers for row in range(len(card))):
                winning_columns = col + 1
                winning_numbers.extend([winning_columns + 5 * i for i in range(5)])
    
    if "3" in patterns:
        corner_count = 0
        # Check the top-left corner (1, 1)
        if card[0][0] in called_numbers:
            corner_count += 1
    
        # Check the top-right corner (1, 5)
        if card[0][4] in called_numbers:
            corner_count += 1
    
        # Check the bottom-left corner (5, 1)
        if card[4][0] in called_numbers:
            corner_count += 1
    
        # Check the bottom-right corner (5, 5)
        if card[4][4] in called_numbers:
            corner_count += 1
    
        if corner_count == 4:
            winning_numbers.extend([1, 5, 21, 25])
            
    if "4" in patterns:        
        inner_corner_count = 0
        # Check the top-left corner (1, 1)
        if card[1][1] in called_numbers:
            inner_corner_count += 1
    
        # Check the top-right corner (1, 5)
        if card[1][3] in called_numbers:
            inner_corner_count += 1
    
        # Check the bottom-left corner (5, 1)
        if card[3][1] in called_numbers:
            inner_corner_count += 1
    
        # Check the bottom-right corner (5, 5)
        if card[3][3] in called_numbers:
            inner_corner_count += 1
    
        if inner_corner_count == 4:
            winning_numbers.extend([7, 9, 17, 19])
    
    remaining_number = True
    if 0 in called_numbers:
        called_numbers.remove(0)
    max_called = called_numbers[-1] if called_numbers else None

    for number in winning_numbers:
        row = (number - 1) // 5
        col = (number - 1) % 5
        if card[row][col] == max_called:
            remaining_number = False
            break
    

    return winning_numbers, remaining_number



@login_required
def block_view(request):
    card_id = request.GET.get('card')
    gameId = request.GET.get('game')
    last_game = Game.objects.get(id=gameId)
    players = json.loads(last_game.playerCard)
    updated_list = [item for item in players if int(item['card']) != int(card_id)]
    last_game.playerCard = json.dumps(updated_list)
    last_game.numberofplayers = len(updated_list)
    last_game.save()
    context ={'message':"Blocked"}
    return JsonResponse(context)

@login_required
def finish_view(request):
    gameId = request.GET.get('game')
    called_numbers_str = request.GET.get('called')

    # Parse the string representation of the list into an actual list
    called_numbers = json.loads(called_numbers_str)

    game = Game.objects.get(id=gameId)
    game.total_calls = len(called_numbers)
    game.played = 'FINISHED'
    game.save()

    context = {'message': "FINISHED"}
    return JsonResponse(context)