from django.shortcuts import render
from utils.query import *
from django.shortcuts import render, redirect
from django.http import HttpResponse
import uuid

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    next = request.GET.get("next")
    if is_authenticated(request):
        role = getrole(request.session["id"])
        # TODO redirect ke dashboard sesuai rolenya
        if role == "atlet":
            return redirect("/atlet/dashboard")
        if role == "pelatih":
            return redirect("/pelatih/dashboard")
        if role == "umpire":
            return redirect("/umpire/dashboard")

    if request.method == 'POST':
        email = request.POST.get('email')
        nama = request.POST.get('name')
        error, result = try_except_query(f"""SELECT id FROM MEMBER WHERE nama='{nama}' and email = '{email}'""") 
        
        if result == []:
            return render(request, 'login.html', context={'errorMsg':'Maaf data tidak ada dalam database'})
        else:
            getId = result
        
        flag = is_authenticated(request)
        if getId!=[] and not flag:
            request.session["nama"] = nama
            request.session["id"] = str(getId[0][0])
            request.session["role"] = getrole(getId[0][0])
            request.session.set_expiry(500)
            request.session.modified = True
            if next != None and next != "None":
                return redirect(next)
            else:
                role = getrole(getId[0][0])
                # TODO redirect ke dashboard sesuai rolenya
                if role == "atlet":
                    return redirect("/atlet/dashboard")
                if role == "pelatih":
                    return redirect("/pelatih/dashboard")
                if role == "umpire":
                    return redirect("/umpire/dashboard")

    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):
    return render(request, 'register.html')

def register_atlet(request):
     # TODO: implement trigger auth
    if request.method == 'POST':
        id = uuid.uuid4()
        name = request.POST.get('name')
        negara = request.POST.get('negara')
        email = request.POST.get('email')
        birthdate = request.POST.get('birthdate')
        play = "FALSE" if (f"{request.POST.get('question1')}"=="on") else "TRUE"
        tinggiBadan = request.POST.get('height')
        gender = "TRUE" if (f"{request.POST.get('question2')}"=="on") else "FALSE"
        # pelatih = request.POST.get('nama_pelatih')
        # worldRank = request.POST.get('nomerhp')
        # status = request.POST.get('nomerhp')
        # totalPoin = request.POST.get('nomerhp')

        emailCheck = execute_query(f"""SELECT * FROM MEMBER WHERE email='{email}'""") 
        if emailCheck==[]:
            execute_query(f"""INSERT INTO MEMBER VALUES ('{id}', '{name}', '{email}');""")
            execute_query(f"""INSERT INTO ATLET VALUES 
                ('{id}', '{birthdate}', '{negara}', {play}, '{tinggiBadan}', NULL, {gender});""")
            execute_query(f"INSERT INTO ATLET_NON_KUALIFIKASI VALUES ('{id}');")
            context = {'message': "Data telah terdaftar", "isSuccess":True}
            return render(request, 'register_pelatih.html', context)
        else:
            print("Email sudah pernah terdaftar")
            context = {'message': "Email sudah pernah terdaftar", "isSuccess":False}
            return render(request, 'register_atlet.html', context)
    
    context = {'message': ""}
    return render(request, "register_atlet.html",context)


def register_pelatih(request):
    if request.method == 'POST':
        id = uuid.uuid4()
        name = request.POST.get('name')
        email = request.POST.get('email')
        startdate = request.POST.get('startdate')
        spesialisasi = {
            "tunggal_putra":request.POST.get('tunggal_putra'),
            "tunggal_putri":request.POST.get('tunggal_putri'),
            "ganda_putra":request.POST.get('ganda_putra'),
            "ganda_putri":request.POST.get('ganda_putri'),
            "ganda_campuran":request.POST.get('ganda_campuran')
        }
        id_spesialisasi = {
            "tunggal_putra":str(execute_query("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Tunggal Putra';")[0][0]),
            "tunggal_putri":str(execute_query("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Tunggal Putri';")[0][0]),
            "ganda_putra":str(execute_query("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Putra';")[0][0]),
            "ganda_putri":str(execute_query("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Putri';")[0][0]),
            "ganda_campuran":str(execute_query("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Campuran';")[0][0])
        }

        ######### TEST #########
        data_pelatih = [id, name, email, startdate, spesialisasi, id_spesialisasi]
        str_data_pelatih = ["id", "name", "email", "startdate", "spesialisasi", "id_spesialisasi"]
        for x in range(len(data_pelatih)):
            print(f"{str_data_pelatih[x]} : {data_pelatih[x]}")
        ########################

        emailCheck = execute_query(f"""SELECT * FROM MEMBER WHERE email='{email}'""") 
        if emailCheck==[]:
            execute_query(f"""INSERT INTO MEMBER VALUES ('{id}', '{name}', '{email}')""")
            execute_query(f"""INSERT INTO PELATIH VALUES ('{id}', '{startdate}')""")
            for key_spesialisasi in spesialisasi:
                if (spesialisasi[key_spesialisasi] is not None):
                    execute_query(f"INSERT INTO PELATIH_SPESIALISASI VALUES ('{id}','{id_spesialisasi[key_spesialisasi]}');")
            context = {'message': "Data telah terdaftar", "isSuccess":True}
            return render(request, 'register_pelatih.html', context)
        else:
            context = {'message': "Email sudah pernah terdaftar", "isSuccess":False}
            return render(request, 'register_pelatih.html', context)

    context = {'message': ""}
    return render(request, "register_pelatih.html",context)


def register_umpire(request):
    # TODO: implement trigger auth
    if request.method == 'POST':
        id = uuid.uuid4()
        name = request.POST.get('name')
        email = request.POST.get('email')
        negara = request.POST.get('negara')

        ######### TEST #########
        data_umpire = [id, name, email, negara]
        str_data_umpire = ["id", "name", "email", "negara"]
        for x in range(len(data_umpire)):
            print(f"{str_data_umpire[x]} : {data_umpire[x]}")
        ########################

        emailCheck = execute_query(f"""SELECT * FROM MEMBER WHERE email='{email}'""") 
        if emailCheck==[]:
            execute_query(f"""INSERT INTO MEMBER VALUES ('{id}', '{name}', '{email}')""")
            execute_query(f"""INSERT INTO UMPIRE VALUES ('{id}', '{negara}')""")
            context = {'message': "Data telah terdaftar", "isSuccess":True}
            return render(request, 'register_umpire.html', context)
        else:
            context = {'message': "Email sudah pernah terdaftar", "isSuccess":False}    
            return render(request, 'register_umpire.html',context)

    context = {'message': ""}
    return render(request, "register_umpire.html",context)

def getrole(Id):
    atletCheck = execute_query(f"""SELECT * FROM atlet WHERE id ='{Id}'""") 
    pelatihCheck = execute_query(f"""SELECT FROM pelatih WHERE id ='{Id}'""") 
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
    
