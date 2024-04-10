from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from account.views import custom_csrf_protect

import random


# Create your views here.
@login_required
def index(request):
    if request.method == 'POST':
        stake = int(request.POST.get("stake"))
        user = request.user
        from account.models import Account
        from game.models import Game
        acc = Account.objects.get(user=user)
        if int(acc.wallet) > stake:
            game = Game.objects.filter(stake=stake,played="Created").order_by('-id').last()
            game2 = Game.objects.filter(stake=stake,played="Started").order_by('-id').last()
            if game2 is not None:
                elapsed_time = (timezone.now() - game2.started_at).total_seconds()
                if elapsed_time < 60:
                    return redirect (pick_card,game2.id)
            if game is not None:
                return redirect (pick_card,game.id)
            new_game = Game.objects.create()
            new_game.stake = int(stake)
            new_game.save_random_numbers(generate_random_numbers())
            new_game.save()
            return redirect (pick_card,new_game.id)
        else:
          return render (request,'game/index.html')

    return render (request,'game/index.html')

@custom_csrf_protect
def telIndex(request):
    if request.method == 'POST':
        stake = int(request.POST.get("stake"))
        user = request.user
        from account.models import Account
        acc = Account.objects.get(user=user)
        from django.db.models import Q
        from game.models import Game
        if int(acc.wallet) > stake:
            game = Game.objects.filter(Q(stake=stake) & (Q(played="Created") | Q(played="Started"))).order_by('-id').last()
            if game is not None:
                return redirect (pick_card,game.id)
            else:
                new_game = Game.objects.create()
                new_game.stake = int(stake)
                new_game.save_random_numbers(generate_random_numbers())
                new_game.save()
                return redirect (pick_card,new_game.id)
        else:
          return render (request,'game/index.html')

    return render (request,'game/index.html')

@login_required
def pick_card(request,gameid):
    from game.models import Game
    game = Game.objects.get(id=int(gameid))
    from account.models import Account
    acc = Account.objects.get(user=request.user)
    if game.played == 'Playing' or game.played == 'Close':
        return redirect(index)
    players = json.loads(game.playerCard)
    if request.user.id in [player_card['user'] for player_card in players]:
        card_id = next(player['card'] for player in players if player['user'] == request.user.id)
        return redirect(bingo,card_id,game.id)
    if request.method == 'POST':
        try:
            cardid = int(request.POST.get("selected_number"))
            time = timezone.now()
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            if cardid not in [player_card['card'] for player_card in players]:
                new_player = {'time': formatted_time, 'card': cardid,'user':request.user.id}
                players.append(new_player)
                game.numberofplayers = game.numberofplayers + 1
                acc.wallet = float(acc.wallet) - float(game.stake)
                acc.save()
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
    return render (request,'game/select_card.html',{'gameid':gameid,'acc':acc},)

@login_required
def get_selected_numbers(request):
    gameid = request.GET.get('paramName', '')
    from game.models import Game
    game = Game.objects.get(id=int(gameid))
    cards = json.loads(game.playerCard)
    # Extract only the card numbers
    card_numbers = [card['card'] for card in cards]

    # Prepare game data
    game_data = {
        "game_id": game.id,
        "stake": str(game.stake),  # Convert Decimal to string
        "number_of_players": game.numberofplayers,
        "winner_price": str(game.winner_price),
        "time_started":str(0)   # Convert Decimal to string
    }

    if game.played == "Started":
        game_data = {
            "game_id": game.id,
            "stake": str(game.stake),  # Convert Decimal to string
            "number_of_players": game.numberofplayers,
            "winner_price": str(game.winner_price),
            "time_started":str(game.started_at)  # Convert Decimal to string
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
    from game.models import Game
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
    from game.models import Card
    cardnumber = request.GET.get('paramName', '')
    card = Card.objects.get(id=int(cardnumber))
    card_numbers = json.loads(card.numbers)
    bingo_table_json = json.dumps(card_numbers)
    return JsonResponse(bingo_table_json,safe=False)

@login_required
def bingo(request,cardid,gameid):
    from game.models import Card, Game
    game = Game.objects.get(id=int(gameid))
    from account.models import Account
    if game:
        acc = Account.objects.get(user=request.user)
        if game.played == 'Playing' or game.played == 'Close':
            return redirect(index)
        players = json.loads(game.playerCard)
        if not request.user.id in [player_card['user'] for player_card in players]:
            return redirect(index)
        if not cardid in [player_card['card'] for player_card in players]:
            if request.user.id in [player_card['user'] for player_card in players]:
                card_id_h = None
                for player in players:
                    if player['user']==request.user.id:
                        card_id_h = player['card']
                if card_id_h:
                    return redirect(bingo,card_id_h,gameid)
            return redirect(index)
        card = Card.objects.get(id=cardid)
        card_numbers = json.loads(card.numbers)
        return render (request,'game/bingo.html',{"card":card_numbers,"gameid":gameid,"cardid":cardid,'acc':acc})
    return redirect(index)


def generate_random_numbers():
    # Generate a list of numbers from 1 to 75
    numbers = list(range(1, 76))
    
    # Shuffle the list to randomize the order
    random.shuffle(numbers)
    
    return numbers


