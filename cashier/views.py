import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from cashier.models import Cashier
from game.models import CashierGame

# Create your views here.

@login_required
def index(request):
    try:
        cashier = Cashier.objects.get(user=request.user)
        if cashier is not None:
            return render (request,'cashier/select_card.html',{'cashier':cashier.name,'shop':cashier.shop.id})
    except:
        return redirect('index')

@login_required
def get_game_stat(request):
    try:
        cashier = Cashier.objects.get(user=request.user)
        if cashier is not None:
            last_cashier_game = CashierGame.objects.filter(user=request.user).order_by('-game__created_at').first()
            if last_cashier_game:
                last_game = last_cashier_game.game

                # Check if the last game's played field is 'STARTED'

                balance = cashier.balance

                context = {
                    'balance':balance,
                    'game': {
                        'id': last_game.id,
                        'played': last_game.played,
                        'stake': last_game.stake
                    },
                }
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

    try:
        # Retrieve the CashierGame object
        cashier_game = get_object_or_404(CashierGame, user=request.user, game_id=gameId)
        
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

    try:
        # Retrieve the CashierGame object
        cashier_game = get_object_or_404(CashierGame, user=request.user, game_id=gameId)
        
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