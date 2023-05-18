from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):
    return render(request, 'register.html')

def register_atlet(request):
    return render(request, 'register_atlet.html')

def register_pelatih(request):
    return render(request, 'register_pelatih.html')

def register_umpire(request):
    return render(request, 'register_umpire.html')