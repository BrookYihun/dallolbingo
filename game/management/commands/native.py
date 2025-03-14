from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import get_current_timezone

class Command(BaseCommand):
    help = 'Update all Game objects with naive created_at to be timezone-aware using SQL'

    def handle(self, *args, **kwargs):
        tz = get_current_timezone()

        with connection.cursor() as cursor:
            self.stdout.write("Updating naive created_at timestamps...")

            # Update only rows with naive datetime
            query = """
                UPDATE game_game
                SET created_at = created_at AT TIME ZONE 'UTC'
                WHERE created_at::TEXT NOT LIKE '%+%';
            """
            cursor.execute(query)
            rows_affected = cursor.rowcount

        self.stdout.write(self.style.SUCCESS(f'{rows_affected} Game objects updated to timezone-aware.'))
