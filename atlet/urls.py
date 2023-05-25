from django.urls import path
from atlet.views import *

app_name = 'atlet'
urlpatterns = [
    path('pertanyaan_kualifikasi/', pertanyaan_kualifikasi, name='pertanyaan_kualifikasi'),
    path('daftar_stadium/', daftar_stadium, name='daftar_stadium'),
    path('daftar_event/<str:stadium>', daftar_event, name='daftar_event'),
    path('pilih_kategori/<str:nama_event>/<int:tahun>', pilih_kategori, name='pilih_kategori'),
    path('unenrolled_event/', unenrolled_event, name='unenrolled_event'),
    path('enrolled_event/', enrolled_event, name='enrolled_event'),
    path('enrolled_event/<str:jenis>/<str:nama_event>/<int:tahun>/', enrolled_event_delete, name='enrolled_event_delete'),
    path('daftar_sponsor/', daftar_sponsor, name='daftar_sponsor'),
    path('list_sponsor/', list_sponsor, name='list_sponsor'),
    path('dashboard/', dashboard, name='dashboard'),
    path('daftar_ujian/', daftar_ujian, name='daftar_ujian'),
    path('pertanyaan_kualifikasi/<int:tahun>/<int:batch>/<str:tempat>/<str:tanggal>/', pertanyaan_kualifikasi, name='pertanyaan_kualifikasi'),
    path('show_riwayat_ujian/', show_riwayat_ujian, name='show_riwayat_ujian'),
    path('enrolled_partai_kompetisi_event/', enrolled_partai_kompetisi_event, name='enrolled_partai_kompetisi_event')
]