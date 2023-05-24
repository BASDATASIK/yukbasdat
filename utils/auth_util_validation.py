from utils.query import *

def throw_to_home_if_unauthorized(request, role):
    if not (check_authorisasi(request, role)):
        request.session["unauthorized"] = f"Anda tidak memiliki akses pada {role}"
        return True 
    return False

def check_authorisasi(request, role):
    if (is_authenticated(request)):
        id_user = request.session["id"]
        if (getrole(id_user) == role):
            return True
    return False

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