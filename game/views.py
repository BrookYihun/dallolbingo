from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from account.models import Account
from game.models import Card, Game
import random

# Create your views here.
@login_required
def index(request):
    if request.method == 'POST':
        stake = int(request.POST.get("stake"))
        user = request.user
        acc = Account.objects.get(user=user)
        if int(acc.wallet) > stake:
            game = Game.objects.filter(stake=stake,played = "Created" ).order_by('-id').last()
            if game is not None:
                return redirect (pick_card,game.id)
            else:
                new_game = Game.objects.create()
                new_game.stake = int(stake)
                new_game.save()
                return redirect (pick_card,new_game.id)
        else:
          return render (request,'game/index.html')

    return render (request,'game/index.html')

@login_required
def pick_card(request,gameid):
    if request.method == 'POST':
        try:
            cardid = int(request.POST.get("selected_number"))
            game = Game.objects.get(id=gameid)
            time = timezone.now()
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            players = json.loads(game.playerCard)
            if cardid not in [player_card['card'] for player_card in players]:
                new_player = {'time': formatted_time, 'card': cardid}
                players.append(new_player)
                game.numberofplayers = game.numberofplayers + 1
            else:
                return render (request,'game/select_card.html',{'gameid':gameid,'message':"Card Taken Pick Again"})

            game.playerCard = json.dumps(players)
            winner = float(game.stake) * float(game.numberofplayers)
            if winner > 100:
                game.admin_cut = winner * 0.2
                game.winner_price =  winner - game.admin_cut
            else:
                game.winner_price = winner
                game.admin_cut = 0

            game.save()
            return redirect (bingo,cardid,game.id)
        except ValueError:
            return HttpResponse('Error')
        
    return render (request,'game/select_card.html',{'gameid':gameid})

@login_required
def get_selected_numbers(request):
    gameid = request.GET.get('paramName', '')
    game = Game.objects.get(id=int(gameid))
    cards = json.loads(game.playerCard)
    # Extract only the card numbers
    card_numbers = [card['card'] for card in cards]

    # Prepare game data
    game_data = {
        "game_id": game.id,
        "stake": str(game.stake),  # Convert Decimal to string
        "number_of_players": game.numberofplayers,
        "winner_price": str(game.winner_price)  # Convert Decimal to string
    }

    # Convert game data to JSON format using DjangoJSONEncoder
    json_game_data = json.dumps(game_data)

    # Construct the response data
    response_data = {
        'selectedNumbers': card_numbers,
        'game': json_game_data
    }
    return JsonResponse(response_data)

@login_required
def get_bingo_stat(request):
    gameid = request.GET.get('paramName', '')
    game = Game.objects.get(id=int(gameid))

    # Prepare game data
    game_data = {
        "game_id": game.id,
        "stake": str(game.stake),  # Convert Decimal to string
        "number_of_players": game.numberofplayers,
        "winner_price": str(game.winner_price)  # Convert Decimal to string
    }

    # Convert game data to JSON format using DjangoJSONEncoder
    json_game_data = json.dumps(game_data)

    # Construct the response data
    response_data = {
        'game': json_game_data
    }
    return JsonResponse(response_data)

@login_required
def get_bingo_card(request):
    cardnumber = request.GET.get('paramName', '')
    card = Card.objects.get(id=int(cardnumber))
    card_numbers = json.loads(card.numbers)
    bingo_table_json = json.dumps(card_numbers)
    return JsonResponse(bingo_table_json,safe=False)

@login_required
def bingo(request,cardid,gameid):
    card = Card.objects.get(id=cardid)
    card_numbers = json.loads(card.numbers)
    return render (request,'game/bingo.html',{"card":card_numbers,"gameid":gameid,"cardid":cardid})

@login_required
def get_random_numbers(request):
    gameid = request.GET.get('paramName', '')
    game = Game.objects.get(id=int(gameid))
    if game.random_numbers == [0]:
        # Generate and save all random numbers if the table is empty
        random_numbers = generate_random_numbers()  # Generate 10 random numbers
        game.save_random_numbers(random_numbers)
        game.save()

    if not game.total_calls == 75:
        random_numbers_list = json.loads(game.random_numbers)
        next_number = random_numbers_list[game.total_calls]
        game.total_calls += 1
        game.save()
        return JsonResponse({'random_number': next_number})
    else:
        return JsonResponse({'message': 'No more random numbers available.'}, status=404)
    
def generate_random_numbers():
    # Generate a list of numbers from 1 to 75
    numbers = list(range(1, 76))
    
    # Shuffle the list to randomize the order
    random.shuffle(numbers)
    
    return numbers

@login_required
def checkBingo(request):
    card_id = request.GET.get('card', '')
    gameid = request.GET.get('game', '')
    game = Game.objects.get(id=int(gameid))
    called_numbers = json.loads(game.random_numbers)

    if not called_numbers:
        context = {'called': called_numbers, 'message': 'No numbers called yet'}
        return render(request, 'game/result.html', context)

    result = []
    players = json.loads(game.playerCard)
    player_cards = [entry['card'] for entry in players]
    card_found = int(card_id) in player_cards
    called_numbers_list = called_numbers
    game.total_calls = len(called_numbers_list)
    game.save()

    if card_found:
        card = Card.objects.get(id=card_id)
        numbers = json.loads(card.numbers)
        winning_columns, winning_rows, winning_diagonals,corner_count,winning_numbers = has_bingo(numbers, called_numbers)
        if len(winning_numbers)>0:
            result.append({'card_name': card.id, 'message': 'Bingo', 'winning_card': numbers, 'winning_rows': winning_rows, 'remaining_numbers': called_numbers_list,'winning_numbers':winning_numbers})
        elif winning_rows!=0:
            result.append({'card_name': card.id, 'message': 'Bingo', 'winning_card': numbers, 'winning_rows': winning_rows, 'remaining_numbers': called_numbers_list})
        elif winning_diagonals!=0:
            result.append({'card_name': card.id, 'message': 'Bingo', 'winning_card': numbers, 'winning_diagonals': winning_diagonals, 'remaining_numbers': called_numbers_list})
        elif winning_columns!=0:
            result.append({'card_name': card.id, 'message': 'Bingo', 'winning_card': numbers, 'winning_columns': winning_columns, 'remaining_numbers': called_numbers_list})
        elif corner_count==4:
            result.append({'card_name': card.id, 'message': 'Bingo', 'winning_card': numbers, 'winning_corners': corner_count, 'remaining_numbers': called_numbers_list})
        else:
            result.append({'card_name': card.id, 'message': 'No Bingo','card':numbers})
    else:
        result.append({'card_name': card_id, 'message': 'Not a Player'})

    context = {'called': called_numbers_list, 'result': result,'game':gameid}
    return  JsonResponse({'random_number': 1})

def has_bingo(card, called_numbers):
    winning_rows = 0
    winning_diagonals = 0
    winning_columns = 0
    called_numbers_list = list(called_numbers)
    corner_count = 0
    winning_numbers = []

    # Check diagonals
    diagonal2 = [card[i][i] for i in range(len(card))]
    diagonal1 = [card[i][len(card) - 1 - i] for i in range(len(card))]
    if all(number in called_numbers for number in diagonal2):
        winning_diagonals = 2
        winning_numbers.append(1)
        winning_numbers.append(7)
        winning_numbers.append(13)
        winning_numbers.append(19)
        winning_numbers.append(25)
        break_index = max([called_numbers_list.index(number) for number in diagonal2 if number in called_numbers_list]) + 1
    if all(number in called_numbers for number in diagonal1):
        winning_diagonals = 1
        winning_numbers.append(5)
        winning_numbers.append(9)
        winning_numbers.append(13)
        winning_numbers.append(17)
        winning_numbers.append(21)
        break_index = max([called_numbers_list.index(number) for number in diagonal1 if number in called_numbers_list]) + 1

    # Check rows
    for row_index, row in enumerate(card):
        if all(number in called_numbers for number in row):
            winning_rows = row_index + 1
            winning_numbers.append((row_index*5)+1)
            winning_numbers.append((row_index*5)+2)
            winning_numbers.append((row_index*5)+3)
            winning_numbers.append((row_index*5)+4)
            winning_numbers.append((row_index*5)+5)
            break_index = max([called_numbers_list.index(number) for number in row if number in called_numbers_list]) + 1

    # Check columns
    for col in range(len(card[0])):
        if all(card[row][col] in called_numbers for row in range(len(card))):
            winning_columns = col + 1
            winning_numbers.append(winning_columns)
            winning_numbers.append(winning_columns+5)
            winning_numbers.append(winning_columns+10)
            winning_numbers.append(winning_columns+15)
            winning_numbers.append(winning_columns+20)
            column = [card[row][col] for row in range(len(card))]
            max_index = max([called_numbers_list.index(number) for number in column if number in called_numbers_list])
            break_index = max_index + 1 if max_index >= 0 else 0

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
        winning_numbers.append(1)
        winning_numbers.append(5)
        winning_numbers.append(21)
        winning_numbers.append(25)

    return winning_columns, winning_rows, winning_diagonals,corner_count,winning_numbers

