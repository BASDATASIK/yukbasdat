from django.urls import path
from atlet.views import *

app_name = 'atlet'
urlpatterns = [
    path('form_data_kualifikasi/', form_data_kualifikasi, name='form_data_kualifikasi'),
    path('pertanyaan_kualifikasi/', pertanyaan_kualifikasi, name='pertanyaan_kualifikasi'),
    path('daftar_event1/', daftar_event1, name='daftar_event1'),
    path('daftar_event2/', daftar_event2, name='daftar_event2'),
    path('pilih_kategori/', pilih_kategori, name='pilih_kategori'),
    path('unenrolled_event/', unenrolled_event, name='unenrolled_event'),
    path('daftar_sponsor/', daftar_sponsor, name='daftar_sponsor'),
    path('dashboard/', dashboard, name='dashboard'),
    path('daftar_ujian/', daftar_ujian, name='daftar_ujian'),
]