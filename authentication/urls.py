from django.urls import path
from authentication.views import *

app_name = 'authentication'
urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]