from django.urls import path

from . import views

urlpatterns = [
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('register/',views.register_view,name="register"),
    path('register_tel/',views.register_tel_view,name="register_tel"),
    path('login_tel/',views.login_tel_view,name="login_tel")
]