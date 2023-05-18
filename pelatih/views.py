from django.shortcuts import render

# Create your views here.
def daftar_atlet(request):
    return render(request, 'daftar_atlet.html')

def list_atlet(request):
    return render(request, 'list_atlet.html')

def list_atlet(request):
    return render(request, 'list_atlet.html')

def dashboard(request):
    return render(request, 'dashboard_pelatih.html')