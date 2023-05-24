from django.urls import path
from pelatih.views import *

app_name = 'pelatih'
urlpatterns = [
    path('daftar_atlet/', daftar_atlet, name='daftar_atlet'),
    path('list_atlet/', list_atlet, name='list_atlet'),
    path('dashboard/', dashboard, name='dashboard'),
    path('latih-atlet/', home_latih_atlet, name='home_latih_atlet'),
    path('latih-atlet/form/', form_latih_atlet, name='form_latih_atlet'),
    path('latih-atlet/list/', list_latih_atlet, name='list_latih_atlet'),
]