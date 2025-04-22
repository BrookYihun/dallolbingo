from django.urls import path

from . import views

urlpatterns = [
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('dashboard/',views.dashboard_view,name="dashboard"),
    path('setting/',views.setting_view,name="setting"),
    path('save-game-settings/', views.save_game_settings, name='save_game_settings'),
]