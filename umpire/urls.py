from django.urls import path
from umpire.views import show_event
from umpire.views import show_result
from umpire.views import show_data_result

app_name = 'umpire'
urlpatterns = [
    path('list-event/', show_event, name='list_event'),
    path('hasil-pertandingan/', show_result, name='hasil_pertandingan'),
    path('data-hasil-pertandingan/', show_data_result, name='data_hasil_pertandingan'),
]