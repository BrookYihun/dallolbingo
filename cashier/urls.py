from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name="cashier"),
    path('get_game_stat/',views.get_game_stat,name="get_game_stat"),
    path('add_player/',views.add_player,name="add_player"),
    path('remove_player/',views.remove_player,name="remove_player")
]