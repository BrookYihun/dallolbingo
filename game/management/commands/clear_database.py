from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Clears all data from the database and resets the auto-increment counters.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing all data from the database and resetting auto-increment counters...')
        
        # Get the database engine
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'sqlite3' in db_engine:
            # Disable foreign key checks for SQLite
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys = OFF;')
        else:
            # Disable foreign key checks for other databases (e.g., MySQL)
            cursor = connection.cursor()
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        
        # Get all models
        all_models = apps.get_models()
        for model in all_models:
            table_name = model._meta.db_table
            self.stdout.write(f'Truncating table {table_name}...')
            cursor.execute(f'DELETE FROM `{table_name}`;')

            if 'sqlite3' in db_engine:
                # Reset auto-increment for SQLite
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
            elif 'mysql' in db_engine:
                # Reset auto-increment for MySQL
                cursor.execute(f'ALTER TABLE `{table_name}` AUTO_INCREMENT = 1;')
        
        if 'sqlite3' in db_engine:
            # Re-enable foreign key checks for SQLite
            cursor.execute('PRAGMA foreign_keys = ON;')
        else:
            # Re-enable foreign key checks for other databases
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')

        self.stdout.write(self.style.SUCCESS('Successfully cleared the database and reset auto-increment counters.'))
