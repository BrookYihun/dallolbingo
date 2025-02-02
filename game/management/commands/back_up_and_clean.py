from django.core.management.base import BaseCommand
from datetime import datetime
import shutil
from django.utils.timezone import make_aware
from game.models import Game

class Command(BaseCommand):
    help = 'Backup the database and remove games played before September 1, 2024'

    def handle(self, *args, **kwargs):
        # Step 1: Backup the database
        self.backup_database()

        # Step 2: Remove games played before September 1, 2024
        self.remove_old_games()

    def backup_database(self):
        # Path to your current SQLite database
        db_path = 'db.sqlite3'

        # Path to the backup file with timestamp
        backup_path = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
        
        try:
            # Create a backup of the database
            shutil.copy(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f"Backup successful. Database saved as {backup_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error while backing up database: {e}"))

    def remove_old_games(self):
        # Define the date threshold (September 1, 2024)
        threshold_date = make_aware(datetime(2024, 11, 20))

        try:
            # Get all games played before the threshold date
            old_games = Game.objects.filter(created_at__lt=threshold_date)
            
            # Count the number of games that will be deleted
            count = old_games.count()

            # Delete the games
            old_games.delete()

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} games played before September 1, 2024."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error while removing old games: {e}"))
