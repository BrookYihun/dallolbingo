from channels.generic.websocket import AsyncWebsocketConsumer
import json
from collections import defaultdict
from asgiref.sync import sync_to_async

shop_states = {}  # e.g. {'shop1': {'game_id': 'abc', 'state': 'started'}}
cashier_cards = defaultdict(dict)  # {'game_id': {'cashier_id': [1, 2, 3]}}
called_numbers = defaultdict(list)  # {'game_id': [1, 23, 45, ...]}

  
# Make the ORM calls asynchronous
@sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.get(id=user_id)

@sync_to_async
def get_cashiers(account):
    from cashier.models import Cashier
    return Cashier.objects.filter(shop=account)


# Fetch a Game by ID
@sync_to_async
def get_game(game_id):
    from game.models import Game
    return Game.objects.get(id=game_id)

# Fetch a Cashier by User ID and Game ID
@sync_to_async
def get_cashier_game(user, game_id):
    from game.models import CashierGame
    return CashierGame.objects.get(user=user, game_id=game_id)

# Save a Game instance
@sync_to_async
def save_game(game):
    game.save()

# Save a CashierGame instance
@sync_to_async
def save_cashier_game(cashier_game):
    cashier_game.save()

# Save an Account instance
@sync_to_async
def save_account(account):
    account.save()

# Save a Cashier instance
@sync_to_async
def save_cashier(cashier):
    cashier.save()

# Fetch an Account by User ID
@sync_to_async
def get_account(user):
    from .models import Account
    return Account.objects.get(user=user)

# Fetch a Cashier by User ID
@sync_to_async
def get_cashier(user):
    from .models import Cashier
    return Cashier.objects.get(user=user)


class CashierGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.shop = self.scope['url_route']['kwargs']['shop']
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.group_name = f'game_{self.game_id}'
        self.cashier_id = str(self.scope['user'].id)

        # Check if this shop already has a game running
        if self.shop in shop_states:
            existing_game_id = shop_states[self.shop]['game_id']
            if existing_game_id != self.game_id:
                # New game detected for this shop: clean up the old game's data
                if existing_game_id in cashier_cards:
                    del cashier_cards[existing_game_id]
                print(f"New game detected for {self.shop}. Cleared cards from old game {existing_game_id}")
        else:
            print(f"No existing game found for shop {self.shop}. Proceeding with game {self.game_id}")

        # Update the shop's game state to the new game
        shop_states[self.shop] = {'game_id': self.game_id, 'state': 'started'}

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Initialize tracking
        if self.game_id not in cashier_cards:
            cashier_cards[self.game_id] = {}

        if self.cashier_id not in cashier_cards[self.game_id]:
            cashier_cards[self.game_id][self.cashier_id] = []

        # Send current game state
        await self.send(text_data=json.dumps({
            'action': 'current_game',
            'game_id': self.game_id,
            'state': shop_states[self.shop]['state']
        }))

        await self.send(text_data=json.dumps({
            'action': 'called_numbers',
            'numbers': called_numbers.get(self.game_id, [])
        }))

        # Send selected cards
        my_cards = cashier_cards[self.game_id].get(self.cashier_id, [])
        others_cards = [
            {
                'cashier_id': cashier,
                'cards': cards
            }
            for cashier, cards in cashier_cards[self.game_id].items()
            if cashier != self.cashier_id
        ]


        await self.send(text_data=json.dumps({
            'action': 'existing_selected_cards',
            'cards_by_cashier': others_cards,
            'selected_cards': my_cards,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        # Do not delete cashier from tracking on disconnect anymore

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('type')

        if action == 'create_game':
            game_id = data.get('game_id')
            shop_states[self.game_id] = {
                'game_id': game_id,
                'state': 'pending'
            }
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'game_created',
                    'game_id': game_id
                }
            )

        elif action == 'start_game':
            try:
                stake = data.get('stake')
                bonus = data.get('bonus') == 'on'
                free = data.get('free') == 'on'

                from datetime import datetime
                from decimal import Decimal
                from cashier.models import Cashier

                user = await get_user(self.cashier_id)
                acc = await get_account(user)

                if acc.prepaid and acc.account < 0:
                    await self.send(text_data=json.dumps({
                        'action': 'error',
                        'message': 'Insufficient prepaid account balance.'
                    }))
                    return

                players_selected = [
                    card for cards in cashier_cards[self.game_id].values() for card in cards
                ]

                cut_per = acc.cut_percentage
                game_id = self.game_id
                game = await get_game(game_id)
                game.stake = int(stake)
                game.played = 'PLAYING'
                game.bonus = bonus
                game.free = free
                await save_game(game)

                time = datetime.now()
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
                players = json.loads(game.playerCard) if game.playerCard else []

                cashiers_qs = await sync_to_async(lambda: Cashier.objects.select_related('user').filter(shop=acc))()
                cashiers = await sync_to_async(list)(cashiers_qs)

                if await sync_to_async(lambda: len(cashiers))() > 1:
                    for cashier in cashiers:
                        cashier_game = await get_cashier_game(cashier.user, game_id)
                        if cashier_game:
                            selected_players_data = []
                            if "_main_cashier" in cashier.user.username:
                                selected_players_data = cashier_cards[self.game_id].get(str(self.cashier_id), [])
                            else:
                                selected_players_data = cashier_cards[self.game_id].get(str(cashier.user.id), [])
                            cashier_game.selected_players = json.dumps(selected_players_data)
                            cashier_game.collected = float(len(cashier_game.get_card_numbers())) * float(stake)
                            await sync_to_async(cashier.increment_balance)(cashier_game.collected)
                            await save_cashier(cashier)
                            await save_cashier_game(cashier_game)

                            for player in json.loads(cashier_game.selected_players):
                                if player not in [p['card'] for p in players]:
                                    players.append({'time': formatted_time, 'card': player})
                                    game.numberofplayers += 1

                    paid = False
                    winner = float(game.stake) * float(game.numberofplayers)
                    if winner > acc.cut_bouldery:
                        winner -= (winner * float(cut_per))

                    for cashier in cashiers:
                        cashier_game = await get_cashier_game(cashier.user, game_id)
                        if cashier.balance > winner:
                            await sync_to_async(cashier.decrement_balance)(winner)
                            cashier_game.pied = winner
                            await save_cashier_game(cashier_game)
                            paid = True
                            break

                    if not paid:
                        for cashier in cashiers:
                            cashier_game = await get_cashier_game(cashier.user, game_id)
                            if cashier.balance <= winner:
                                winner -= float(cashier.balance)
                                cashier_game.pied = cashier.balance
                                await sync_to_async(cashier.decrement_balance)(cashier.balance)
                                await save_cashier_game(cashier_game)
                            elif cashier.balance > winner:
                                await sync_to_async(cashier.decrement_balance)(winner)
                                cashier_game.pied = winner
                                await save_cashier_game(cashier_game)
                                break
                else:
                    for player in players_selected:
                        if player not in [p['card'] for p in players]:
                            players.append({'time': formatted_time, 'card': player})
                            game.numberofplayers += 1

                game.playerCard = json.dumps(players)
                winner = float(game.stake) * float(game.numberofplayers)

                if winner > acc.cut_bouldery:
                    game.shop_cut = float(winner) * float(cut_per)
                    game.winner_price = winner - game.shop_cut
                    game.admin_cut = game.shop_cut * float(acc.percentage)
                else:
                    game.shop_cut = 0
                    game.winner_price = winner
                    game.admin_cut = 0

                if winner > acc.cut_bouldery:
                    acc.account -= Decimal(game.admin_cut)
                    acc.total_earning += Decimal(str(game.shop_cut))
                    acc.net_earning += Decimal(str(game.shop_cut - game.admin_cut))
                    await save_account(acc)

                if game.free and game.numberofplayers >= 30:
                    game.winner_price -= float(game.stake)

                await save_game(game)

                # Notify front-end the game has started
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'game_started',
                        'game_id': game_id
                    }
                )

                await self.send(text_data=json.dumps({
                    'action': 'success',
                    'message': 'Game started successfully.'
                }))

            except Exception as e:
                print(e)
                await self.send(text_data=json.dumps({
                    'action': 'error',
                    'message': f'Failed to start game: {str(e)}'
                }))


        elif action == 'end_game':
            if self.game_id in shop_states:
                shop_states[self.game_id]['state'] = 'ended'
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'game_ended',
                        'game_id': shop_states[self.game_id]['game_id']
                    }
                )

        elif action == 'add_player':
            card_id = data.get('card')
            if self.cashier_id in cashier_cards[self.game_id]:
                if card_id not in cashier_cards[self.game_id][self.cashier_id]:
                    cashier_cards[self.game_id][self.cashier_id].append(card_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'player_added',
                    'card': card_id,
                    'by': self.scope['user'].username
                }
            )

        elif action == 'remove_player':
            card_id = data.get('card')
            if self.cashier_id in cashier_cards[self.game_id]:
                if card_id in cashier_cards[self.game_id][self.cashier_id]:
                    cashier_cards[self.game_id][self.cashier_id].remove(card_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'player_removed',
                    'card': card_id,
                    'by': self.scope['user'].username
                }
            )
        
        elif action == 'start_auto_play':
            game_id = data.get("game_id")
            await self.start_auto_play_to_group(game_id)

        elif action == 'stop_auto_play':
            game_id = data.get("game_id")
            await self.stop_auto_play_to_group(game_id)
            

        elif action == "called_number":
            number = data.get("number")
            game_id = data.get("game_id")

            if number is None or game_id is None:
                await self.send(text_data=json.dumps({
                    'action': 'error',
                    'message': 'Invalid number or game ID.'
                }))
                return

            # Only add if not already called
            if number not in called_numbers[game_id]:
                called_numbers[game_id].append(number)

                # Broadcast to all cashiers in the shop group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "number_called",
                        "number": number,
                        "game_id": game_id
                    }
                )
        
        elif action == 'check_bingo_request':
            number = data.get('number')
            game_id = data.get('game_id')

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_check_bingo_request',
                    'number': number,
                    'game_id': game_id,
                }
            )

        elif action == 'check_bingo_result':
            result = data.get('result')
            game = data.get('game')

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_check_bingo_result',
                    'result': result,
                    'game': game,
                }
            )

        elif action == 'close_bingo_result':
            card_name = data.get('card_name')
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'bingo_result_closed',
                    'card_name': card_name,
                }
            )

    
    async def start_auto_play_to_group(self, game_id):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "auto_play_started",
                "message": f"Auto play started for game {game_id}"
            }
        )

    async def stop_auto_play_to_group(self, game_id):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "auto_play_stoped",
                "message": f"Auto play stoped for game {game_id}"
            }
        )

    # Event handlers
    async def game_created(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_created',
            'game_id': event['game_id']
        }))

    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_started',
            'game_id': event['game_id']
        }))

    async def game_ended(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_ended',
            'game_id': event['game_id']
        }))

    async def player_added(self, event):
        await self.send(text_data=json.dumps({
            'action': 'player_added',
            'card': event['card'],
            'by': event['by']
        }))

    async def player_removed(self, event):
        await self.send(text_data=json.dumps({
            'action': 'player_removed',
            'card': event['card'],
            'by': event['by']
        }))
    
    async def auto_play_started(self, event):
        await self.send(text_data=json.dumps({
            "action": "auto_play_started",
            "message": event["message"]
        }))
    
    async def auto_play_stoped(self, event):
        await self.send(text_data=json.dumps({
            "action": "auto_play_stoped",
            "message": event["message"]
        }))

    async def number_called(self, event):
        await self.send(text_data=json.dumps({
            "action": "number_called",
            "number": event["number"],
            "game_id": event["game_id"]
        }))

    
    async def send_check_bingo_request(self, event):
        await self.send(text_data=json.dumps({
            'type': 'check_bingo_request',
            'number': event['number'],
            'game_id': event['game_id'],
        }))

    async def send_check_bingo_result(self, event):
        await self.send(text_data=json.dumps({
            'type': 'check_bingo_result',
            'result': event['result'],
            'game': event['game'],
        }))

    async def bingo_result_closed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'bingo_result_closed',
            'card_name': event['card_name'],
        }))