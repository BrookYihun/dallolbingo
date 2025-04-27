from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'backup/ws/game/(?P<shop>\w+)/(?P<game_id>\w+)/$', consumers.CashierGameConsumer.as_asgi()),
]