import random
from django.core.management.base import BaseCommand
from game.models import Card
import json

def generate_bingo_card():
    bingo_card = []
    used_numbers = set()

    for i in range(5):
        row = []
        for j in range(5):
            if i == 2 and j == 2:
                row.append(0)
            else:
                lower_bound = j * 15 + 1
                upper_bound = (j + 1) * 15
                num = random.randint(lower_bound, upper_bound)
                while num in used_numbers:
                    num = random.randint(lower_bound, upper_bound)
                used_numbers.add(num)
                row.append(num)
        bingo_card.append(row)
    return bingo_card

class Command(BaseCommand):
    def handle(self, *args, **options):
        used_cards = set()
        unique_count = 0
        total_cards = 1000

        # Generate and check 1000 unique bingo cards
        while unique_count < total_cards:
            bingo_card = generate_bingo_card()
            card_json = json.dumps(bingo_card)
            
            if card_json not in used_cards:
                used_cards.add(card_json)
                unique_count += 1
            else:
                print("Duplicate card found, regenerating...")
        
        # Store the unique cards in the database
        num = 1
        for card_json in used_cards:
            bingo_card_model = Card.objects.get(id=num)
            bingo_card_model.numbers = card_json
            bingo_card_model.save()
            num+=1

        self.stdout.write(self.style.SUCCESS('Successfully generated and stored 1000 unique bingo cards.'))
