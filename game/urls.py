from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('tel/',views.telIndex,name="telIndex"),
    path('pick/<int:gameid>/',views.pick_card,name="pick"),
    path('get-selected-numbers/', views.get_selected_numbers, name='get_selected_numbers'),
    path('get-bingo-card/', views.get_bingo_card, name='get_bingo_card'),
    path('get-bingo-stat/',views.get_bingo_stat,name="get_bingo_stat"),
    path('bingo/<int:cardid>/<int:gameid>',views.bingo,name="bingo"),
]