from django.shortcuts import render

# Create your views here.
def form_data_kualifikasi(request):
    return render(request, 'form_data_kualifikasi.html')

def pertanyaan_kualifikasi(request):
    return render(request, 'pertanyaan_kualifikasi.html')

def daftar_event1(request):
    return render(request, 'daftar_event1.html')

def daftar_event2(request):
    return render(request, 'daftar_event2.html')

def pilih_kategori(request):
    return render(request, 'pilih_kategori.html')
