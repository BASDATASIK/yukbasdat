from django.shortcuts import render

from pelatih.forms import PendaftaranAtlet
from utils.query import *

# Create your views here.
def daftar_atlet(request):
    return render(request, 'daftar_atlet.html')

def list_atlet(request):
    return render(request, 'list_atlet.html')

def list_atlet(request):
    return render(request, 'list_atlet.html')

# Parameter id_pelatih hanya sementara, harusnya diambil dari session
def home_latih_atlet(request, id_pelatih):
    return render(request, 'home_latih_atlet.html', context={'id_pelatih':id_pelatih})

def form_latih_atlet(request, id_pelatih):
    ###### INITIALIZE TRIGGER ######
    ############################################
    query_create_function_1 = '''
    CREATE FUNCTION IS_TRAINED() RETURNS trigger AS
    $$
    DECLARE
        count_latih INTEGER;
    BEGIN 
        SELECT COUNT(*) INTO count_latih
        FROM atlet_pelatih AP
        WHERE (AP.id_pelatih = NEW.id_pelatih) AND (AP.id_atlet = NEW.id_atlet);
        
        IF (count_latih > 0) THEN
            RAISE EXCEPTION 'Atlet sudah kau latih';
        END IF;
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    '''
    try_except_query(query_create_function_1)
    query_create_trigger_1 = '''
    CREATE TRIGGER check_apakah_atlet_sudah_melatih
    BEFORE INSERT OR UPDATE ON atlet_pelatih
    FOR EACH ROW
    WHEN ((NEW.id_pelatih IS NOT NULL) AND (NEW.id_atlet IS NOT NULL))
    EXECUTE FUNCTION IS_TRAINED();
    '''
    try_except_query(query_create_trigger_1)
    ############################################
    query_create_function_2 = '''
    CREATE FUNCTION IS_MORE_THAN_TWO() RETURNS trigger AS
    $$
    DECLARE
        count_pelatih INTEGER;
        remove_id_pelatih UUID;
    BEGIN 
        SELECT COUNT(DISTINCT AP.id_pelatih) INTO count_pelatih
        FROM atlet_pelatih AP 
        WHERE (AP.id_atlet = NEW.id_atlet);
        
        IF (count_pelatih >= 2) THEN
            SELECT AP.id_pelatih INTO remove_id_pelatih
            FROM atlet_pelatih AP 
            WHERE (AP.id_atlet = NEW.id_atlet)
            LIMIT 1;

            RAISE EXCEPTION 'Atlet sudah dilatih 2 pelatih. Removing salah satu ... -> SUCCESS';
        END IF;
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    '''
    try_except_query(query_create_function_2)
    query_create_trigger_2 = '''
    CREATE TRIGGER check_apakah_atlet_sudah_punya_dua_pelatih
    BEFORE INSERT OR UPDATE ON atlet_pelatih
    FOR EACH ROW
    WHEN (NEW.id_atlet IS NOT NULL)
    EXECUTE FUNCTION IS_MORE_THAN_TWO();
    '''
    try_except_query(query_create_trigger_2)
    ############################################
    query_deletion = '''
    CREATE FUNCTION delete_atlet_pelatih(except_id UUID, id_atlet_Par UUID) RETURNS VOID AS
    $$
    DECLARE
        remove_id_pelatih UUID;
    BEGIN 
        SELECT AP.id_pelatih INTO remove_id_pelatih
        FROM atlet_pelatih AP 
        WHERE (AP.id_atlet = id_atlet_Par) AND (AP.id_pelatih != except_id)
        LIMIT 1;

        DELETE FROM atlet_pelatih
        WHERE (id_atlet = id_atlet_Par) AND (id_pelatih = remove_id_pelatih);
    END;
    $$ LANGUAGE plpgsql;
    '''
    try_except_query(query_deletion)
    ##############################

    errorFlag, errorMsg = False, None
    print(request.method) # PRINT
    if request.method == 'POST':
        form = PendaftaranAtlet(request.POST)
        if form.is_valid():
            selected_option = form.cleaned_data['dropdown']
            if (selected_option != '$not_complete$'):
                errorFlag, queryResult = try_except_query(f"INSERT INTO atlet_pelatih VALUES ('{id_pelatih}','{selected_option}');")
                if (errorFlag):
                    errorMsg = str(queryResult).split("CONTEXT:")[0]
                if (str(errorMsg).startswith("Atlet sudah dilatih 2 pelatih")):
                    try_except_query(f"SELECT delete_atlet_pelatih('{id_pelatih}', '{selected_option}');")
                    try_except_query(f"INSERT INTO atlet_pelatih VALUES ('{id_pelatih}','{selected_option}');")
            else:
                errorFlag = True
                errorMsg = 'Data yang diisikan belum lengkap, silahkan lengkapi data terlebih dahulu'
            print(selected_option) # PRINT
    else:
        form = PendaftaranAtlet()
    
    print(errorFlag)
    context = {
        'form': form,
        'errorFlagBefore': errorFlag,
        'errorMsgBefore': errorMsg,
        'isEndswithSuccess': str(errorMsg).strip().endswith("SUCCESS")
    }
    return render(request, 'form_latih_atlet_pelatih.html', context)

def list_latih_atlet(request, id_pelatih):
    query_list_latih = f'''
    SELECT 
        MA.nama, MA.email, A.world_rank
    FROM 
        atlet A 
        INNER JOIN atlet_pelatih AP ON (A.id = AP.id_atlet)
        INNER JOIN pelatih P ON (P.id = AP.id_pelatih)
        INNER JOIN member MA ON (A.id = MA.id)
    WHERE
        P.id = '{id_pelatih}';
    '''
    list_list_latih = list_tup_to_list_list(execute_query(query_list_latih))
    for row in list_list_latih:
        row[2] = "" if (row[2] is None) else row[2]
    context = {
        'list_list_latih': list_list_latih
    }
    return render(request, 'list_latih_atlet.html', context)

