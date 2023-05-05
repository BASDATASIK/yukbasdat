from django.urls import path
from umpire.views import show_event

app_name = 'umpire'
urlpatterns = [
    path('list-event/', show_event, name='login'),
]