from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('pick/<int:gameid>/',views.pick_card,name="pick"),
    path('get-selected-numbers/', views.get_selected_numbers, name='get_selected_numbers'),
    path('get-bingo-card/', views.get_bingo_card, name='get_bingo_card'),
    path('get-bingo-stat/',views.get_bingo_stat,name="get_bingo_stat"),
    path('get-random-numbers/',views.get_random_numbers,name="get_random_numbers"),
    path('checkBingo/',views.checkBingo,name="checkBingo"),
    path('bingo/<int:cardid>/<int:gameid>',views.bingo,name="bingo"),
]