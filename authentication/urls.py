from django.urls import path
from authentication.views import *

app_name = 'authentication'
urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register_atlet/', register_atlet, name='register-atlet'),
    path('register_pelatih/', register_pelatih, name='register-pelatih'),
    path('register_umpire/', register_umpire, name='register-umpire'),
    path('logout/', logout, name='logout'),
]