from django.urls import path
from umpire.views import show_event
from umpire.views import show_result
from umpire.views import show_data_result
from umpire.views import *

app_name = 'umpire'
urlpatterns = [
    path('list-event/', show_event, name='list_event'),
    path('hasil-pertandingan/', show_result, name='hasil_pertandingan'),
    path('data-hasil-pertandingan/', show_data_result, name='data_hasil_pertandingan'),
    path('pertandingan/semifinal/', pertandingan_semifinal, name='pertandingan_semifinal'),
    path('pertandingan/final/', pertandingan_final, name='pertandingan_final'),
    path('data-perolehan-poin/', data_perolehan_poin, name='data_perolehan_poin'),
]