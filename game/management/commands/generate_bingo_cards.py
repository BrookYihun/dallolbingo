from django.core.management.base import BaseCommand
import json

from game.models import Card

class Command(BaseCommand):
    help = 'Import cards from num.txt'

    def handle(self, *args, **kwargs):
        filename = 'num.txt'  # Assuming num.txt is in the same directory as this script
        with open(filename, "r") as file:
            for line in file:
                numbers = json.loads(line.strip())
                card = Card.objects.create(numbers=numbers)
                self.stdout.write(self.style.SUCCESS(f"Card {card.id} created successfully"))
                card.save()
