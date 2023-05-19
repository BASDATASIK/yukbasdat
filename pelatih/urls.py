from django.urls import path
from pelatih.views import *

app_name = 'pelatih'
urlpatterns = [
    path('daftar_atlet/', daftar_atlet, name='daftar_atlet'),
    path('list_atlet/', list_atlet, name='list_atlet'),
    path('latih-atlet/<str:id_pelatih>', home_latih_atlet, name='home_latih_atlet'),
    path('latih-atlet/form/<str:id_pelatih>', form_latih_atlet, name='form_latih_atlet'),
    path('latih-atlet/list/<str:id_pelatih>', list_latih_atlet, name='list_latih_atlet'),
]