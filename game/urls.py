from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('new-game/',views.new_game_view,name="new_game"),
    path('check/',views.check_winner_view,name='check'),
    path('block/',views.block_view,name='block'),
    path('get_game_stat/',views.game_stat,name="game_stat"),
    path('add_player/',views.add_player,name="main_add_player"),
    path('remove_player/',views.remove_player,name="main_remove_player"),
    path('update_stake/',views.update_stake,name="update_stake"),
    path('finish/',views.finish_view,name="finish")
]