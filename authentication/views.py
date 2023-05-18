from django.shortcuts import render
from utils.query import *
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    next = request.GET.get("next")
    # if is_authenticated(request):
    #     role = getrole(request.session["id"])
    #     # TODO redirect ke dashboard sesuai rolenya
    #     if role == "atlet":
    #         return redirect("/dashboard/atlet")
    #     if role == "pelatih":
    #         return redirect("/dashboard/pelatih")
    #     if role == "umpire":
    #         return redirect("/dashboard/umpire")

    if request.method == 'POST':
        email = request.POST.get('email')
        nama = request.POST.get('name')
        getId = execute_query(f"""SELECT id FROM MEMBER WHERE nama='{nama}' and email = '{email}'""") 
        flag = is_authenticated(request)
        if getId!=[] and not flag:
            request.session["nama"] = nama
            request.session["id"] = getId[0][0]
            request.session["role"] = getrole(getId[0][0])
            request.session.set_expiry(500)
            request.session.modified = True
            if next != None and next != "None":
                return redirect(next)
            else:
                role = getrole(getId[0][0])
                if role == "atlet":
                    return redirect("/dashboard/atlet")
                if role == "pelatih":
                    return redirect("/dashboard/pelatih")
                if role == "umpire":
                    return redirect("/dashboard/umpire")

    return render(request, 'login.html')

def getrole(Id):
    atletCheck = execute_query(f"""SELECT * FROM atlet WHERE id ='{Id}'""") 
    pelatihCheck = execute_query(f"""SELECT * FROM pelatih WHERE id ='{Id}'""") 
    umpireCheck = execute_query(f"""SELECT * FROM umpire WHERE id ='{Id}'""") 

    if atletCheck!=[]:
        return "atlet"
    if pelatihCheck!=[]:
        return "pelatih"
    if umpireCheck!=[]:
        return "umpire"
    
def is_authenticated(request):
    try:
        request.session["id"]
        return True
    except KeyError:
        return False
    
def logout(request):
    next = request.GET.get("next")

    if not is_authenticated(request):
        return redirect("/")

    request.session.flush()
    request.session.clear_expired()

    if next != None and next != "None":
        return redirect(next)
    else:
        return redirect("/")
    
def register_admin(request):
    # TODO: implement trigger auth
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        nomerhp = request.POST.get('nomerhp')