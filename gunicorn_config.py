# gunicorn_config.py

import os
import django

def post_fork(server, worker):
    # Initialize Django in the worker process
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dallolbingo.settings')
    django.setup()
