from django.shortcuts import render
from django.shortcuts import redirect
from utils.query import *
from django.http import HttpResponseRedirect
from django.urls import reverse
import ast

# Create your views here.
def show_event(request):
    return render(request, 'list_event.html')

def show_result(request):
    return render(request, 'hasil_pertandingan.html')

def show_data_result(request):
    #print( request.session["id"])
    return render(request, 'data_hasil_pertandingan.html')

def show_riwayat_ujian(request):
    query = """
            SELECT nama, tahun, batch, tempat, tanggal, hasil_lulus
            FROM atlet_nonkualifikasi_ujian_kualifikasi
            JOIN member m on m.id = atlet_nonkualifikasi_ujian_kualifikasi.id_atlet;
            """
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'riwayat_ujian_umpire.html', {'riwayat_ujian': result})

def pertandingan_semifinal(request):
    value = request.COOKIES.get('peserta_menang')
    res = value.strip("]['").split("', '")
    print(res)
    list_skor = {}
    list_nama = []
    for i in range(0,len(res)):
        list_skor.update({res[i] : 0})
    for i in range(0,len(res),2):
        sublist = [res[i], res[i+1]]
        list_nama.append(sublist)
    context = {
        'list_nama' : list_nama,
        'list_skor' : list_skor,
        }

    if request.method == "POST":
        hasil = request.POST['hasil_match']
        hasil_dict = ast.literal_eval(hasil)
        list_menang = []
        list_kalah = []
        print(hasil_dict)
        for i in list_nama:
            if (hasil_dict[i[0]]>=20 and hasil_dict[i[1]]>=20 and hasil_dict[i[0]]==hasil_dict[i[1]]+2):
                list_menang.append(i[0])
                list_kalah.append(i[1])
            elif (hasil_dict[i[0]]>=20 and hasil_dict[i[1]]>=20 and hasil_dict[i[1]]==hasil_dict[i[0]]+2):
                list_kalah.append(i[1])
                list_menang.append(i[0])
            elif(hasil_dict[i[0]] == 21):
                list_kalah.append(i[1])
                list_menang.append(i[0])
            elif(hasil_dict[i[1]] == 21):
                list_kalah.append(i[0])
                list_menang.append(i[1])
        res = HttpResponseRedirect(reverse('umpire:pertandingan_final'))
        res.set_cookie('peserta_menang_semifinal', list_menang)
        res.set_cookie('peserta_kalah_semifinal', list_kalah)
        return res
    return render(request, 'pertandingan_semifinal.html', context)

def pertandingan_final(request):
    value = request.COOKIES.get('peserta_menang_semifinal')
    res = value.strip("]['").split("', '")
    list_skor_menang = {}
    list_nama_menang = []
    for i in range(0,len(res)):
        list_skor_menang.update({res[i] : 0})
    for i in range(0,len(res),2):
        sublist = [res[i], res[i+1]]
        list_nama_menang.append(sublist)
    
    value = request.COOKIES.get('peserta_kalah_semifinal')
    res = value.strip("]['").split("', '")
    list_skor_kalah = {}
    list_nama_kalah = []
    for i in range(0,len(res)):
        list_skor_kalah.update({res[i] : 0})
    for i in range(0,len(res),2):
        sublist = [res[i], res[i+1]]
        list_nama_kalah.append(sublist)

    context = {
        'list_nama_menang' : list_nama_menang,
        'list_skor_menang' : list_skor_menang,
        'list_nama_kalah' : list_nama_kalah,
        'list_skor_kalah' : list_skor_kalah,
        }
    
    return render(request, 'pertandingan_final.html', context)

def data_perolehan_poin(request):
    return render(request, 'data_perolehan_poin.html')

def dashboard(request):
    return render(request, 'dashboard_umpire.html')

def create_ujian(request):
    if request.method == 'POST':
        # retrieve data from post request
        tahun = request.POST.get('tahun')
        batch = request.POST.get('batch')
        tempat = request.POST.get('location')
        tanggal = request.POST.get('date')

        # form validation
        if not tahun or not batch or not tempat or not tanggal:
            msg = 'Data yang diisikan belum lengkap, silahkan lengkapi data terlebih dahulu'
            return render(request, 'form_buat_ujian_kualifikasi.html', {'msg': msg})

        # create ujian
        query = f"INSERT INTO ujian_kualifikasi (tahun, batch, tempat, tanggal) VALUES ('{tahun}', '{batch}', '{tempat}', '{tanggal}')"
        error, result = try_except_query(query)
        if error:
            msg = "Field yang diisi tidak valid, silahkan isi kembali dengan benar"
            return render(request, 'form_buat_ujian_kualifikasi.html', {'msg': msg})
        else:
            return redirect('umpire:daftar_ujian')
            
    return render(request, 'form_buat_ujian_kualifikasi.html', {'msg': ''})

def daftar_ujian(request):
    list_ujian = execute_query(
        '''
        SELECT * FROM ujian_kualifikasi;
        '''
    )
    list_ujian = list_tup_to_list_list(list_ujian)
    return render(request, 'list_ujian_kualifikasi_umpire.html', {'list_ujian': list_ujian})

def pertandingan_perempatfinal(request):
    query_pertandingan = '''
SELECT DISTINCT
    CASE
        WHEN jenis_partai LIKE '%D' THEN CONCAT(M.nama, ' & ', M2.nama)
        WHEN jenis_partai LIKE '%S' THEN M.nama
    END AS nama_peserta
FROM
    partai_peserta_kompetisi PPK
    JOIN peserta_kompetisi PK ON PPK.nomor_peserta = PK.nomor_peserta
    JOIN atlet_ganda AG ON PK.id_atlet_ganda = AG.id_atlet_ganda
    JOIN atlet_kualifikasi AK ON AG.id_atlet_kualifikasi = AK.id_atlet
    JOIN atlet_kualifikasi AK2 ON AG.id_atlet_kualifikasi_2 = AK2.id_atlet
    JOIN atlet A ON AK.id_atlet = A.id
    JOIN atlet A2 ON AK2.id_atlet = A2.id
    JOIN member M ON A.id = M.id
    JOIN member M2 ON A2.id = M2.id
WHERE
    jenis_partai LIKE '%D' OR jenis_partai LIKE '%S'
LIMIT 8;    
'''
    query_atlet_ganda = '''
    select distinct concat(M.nama, ' & ', M2.nama) as nama_peserta 
    from partai_peserta_kompetisi PPK 
    join peserta_kompetisi PK on PPK.nomor_peserta = PK.nomor_peserta 
    join atlet_ganda AG on (PK.id_atlet_ganda = AG.id_atlet_ganda) 
    join atlet_kualifikasi AK on (AG.id_atlet_kualifikasi = AK.id_atlet) 
    join atlet_kualifikasi AK2 on (AG.id_atlet_kualifikasi_2 = AK2.id_atlet) 
    join atlet A on (AK.id_atlet = A.id) join atlet A2 on (AK2.id_atlet = A2.id) 
    join member M on (A.id = M.id) 
    join member M2 on (A2.id = M2.id) 
    where jenis_partai LIKE '%D' LIMIT 4;
    '''

    query_atlet_single = '''
    select distinct M.nama as nama_peserta 
    from partai_peserta_kompetisi PPK 
    join peserta_kompetisi PK on PPK.nomor_peserta = PK.nomor_peserta 
    join atlet_kualifikasi AK on (PK.id_atlet_kualifikasi = AK.id_atlet) 
    join atlet A on (AK.id_atlet = A.id) join member M on (A.id = M.id) 
    where jenis_partai LIKE '%S' LIMIT 4;
    '''

    #list_atlet_kualifikasi = list_tup_to_list_list(execute_query(query_pertandingan))
    list_atlet_ganda = list_tup_to_list_list(execute_query(query_atlet_ganda))
    list_atlet_single = list_tup_to_list_list(execute_query(query_atlet_single))
    list_atlet_kualifikasi = list_atlet_ganda + list_atlet_single
    list_skor = {}
    list_nama = []
    for i in range(0,len(list_atlet_kualifikasi)):
        list_skor.update({list_atlet_kualifikasi[i][0] : 0})
    for i in range(0,len(list_atlet_kualifikasi),2):
        sublist = [list_atlet_kualifikasi[i][0], list_atlet_kualifikasi[i+1][0]]
        list_nama.append(sublist)
    context = {
        'list_nama' : list_nama,
        'list_skor' : list_skor,
    }
    if request.method == "POST":
        hasil = request.POST['hasil_match']
        hasil_dict = ast.literal_eval(hasil)
        list_menang = []
        for i in list_nama:
            if (hasil_dict[i[0]]>=20 and hasil_dict[i[1]]>=20 and hasil_dict[i[0]]==hasil_dict[i[1]]+2):
                list_menang.append(i[0])
            elif (hasil_dict[i[0]]>=20 and hasil_dict[i[1]]>=20 and hasil_dict[i[1]]==hasil_dict[i[0]]+2):
                list_menang.append(i[1])
            elif(hasil_dict[i[0]] == 21):
                list_menang.append(i[0])
            elif(hasil_dict[i[1]] == 21):
                list_menang.append(i[1])
        res = HttpResponseRedirect(reverse('umpire:pertandingan_semifinal'))
        res.set_cookie('peserta_menang', list_menang)
        return res
    return render(request, 'pertandingan_perempatfinal.html', context)


def daftar_atlet(request):
    query_atlet_kualifikasi = '''
    SELECT 
        M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, AK.world_rank, AK.world_tour_rank, 
        A.jenis_kelamin, COALESCE(SUM(PH.total_point),0) AS total_point_all_time
    FROM
        atlet A
        INNER JOIN atlet_kualifikasi AK ON (AK.id_atlet = A.id)
        LEFT OUTER JOIN point_history PH ON (PH.id_atlet = A.id)
        INNER JOIN member M ON (A.id = M.id)
    GROUP BY
        M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, AK.world_rank, AK.world_tour_rank, A.jenis_kelamin;
    '''
    list_atlet_kualifikasi = list_tup_to_list_list(execute_query(query_atlet_kualifikasi))
    for row in list_atlet_kualifikasi:
        row[1] = row[1].strftime("%d %B %Y")
        row[7] = 'Laki-laki' if (row[7]) else 'Perempuan'

    query_atlet_non_kualifikasi = '''
    SELECT 
        M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, '-' AS world_rank,
        A.jenis_kelamin, COALESCE(SUM(PH.total_point),0) AS total_point_all_time
    FROM
        atlet A
        INNER JOIN atlet_non_kualifikasi ANK ON (ANK.id_atlet = A.id)
        LEFT OUTER JOIN point_history PH ON (PH.id_atlet = A.id)
        INNER JOIN member M ON (A.id = M.id)
    GROUP BY
        M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, world_rank, A.jenis_kelamin;
    '''
    list_atlet_non_kualifikasi = list_tup_to_list_list(execute_query(query_atlet_non_kualifikasi))
    for row in list_atlet_non_kualifikasi:
        row[1] = row[1].strftime("%d %B %Y")
        row[6] = 'Laki-laki' if (row[6]) else 'Perempuan'

    query_atlet_ganda = '''
    SELECT
        AG.id_atlet_ganda, M1.nama AS nama_atlet_1, M2.nama AS nama_atlet_2, 
        COALESCE(SUM(PH1.total_point+PH2.total_point),0) AS jumlah_total_point_kedua
    FROM
        atlet_ganda AG 
        INNER JOIN member M1 ON (AG.id_atlet_kualifikasi = M1.id)
        INNER JOIN member M2 ON (AG.id_atlet_kualifikasi_2 = M2.id)
        LEFT OUTER JOIN point_history PH1 ON (PH1.id_atlet = AG.id_atlet_kualifikasi)
        LEFT OUTER JOIN point_history PH2 ON (PH2.id_atlet = AG.id_atlet_kualifikasi_2)
    GROUP BY 
        AG.id_atlet_ganda, nama_atlet_1, nama_atlet_2;
    '''
    list_atlet_ganda = list_tup_to_list_list(execute_query(query_atlet_ganda))

    context = {
        'list_atlet_kualifikasi':list_atlet_kualifikasi,
        'list_atlet_non_kualifikasi':list_atlet_non_kualifikasi,
        'list_atlet_ganda':list_atlet_ganda
    }
    return render(request, 'daftar_atlet_umpire.html', context)

def partai_kompetisi_event(request):
    query_partai_kompetisi_event = '''
    SELECT 
        E.nama_event, PaK.tahun_event, S.nama AS stadium, PaK.jenis_partai, 
        E.kategori_superseries, E.tgl_mulai, E.tgl_selesai, count(PPK.nomor_peserta) as kapasitas, '' AS action
    FROM 
        partai_kompetisi PaK 
        INNER JOIN event E ON (PaK.nama_event = E.nama_event AND PaK.tahun_event = E.tahun)
        INNER JOIN stadium S ON (E.nama_stadium = S.nama)
        LEFT OUTER JOIN partai_peserta_kompetisi PPK ON (PPK.jenis_partai = PaK.jenis_partai AND PPK.nama_event = PaK.nama_event AND PPK.tahun_event = PaK.tahun_event)
    GROUP BY 
        E.nama_event, PaK.tahun_event, stadium, PaK.jenis_partai, 
        E.kategori_superseries, E.tgl_mulai, E.tgl_selesai, action
    ORDER BY 
        PaK.tahun_event DESC, E.tgl_mulai DESC, E.nama_event, PaK.jenis_partai;
    '''
    list_partai_kompetisi_event = list_tup_to_list_list(execute_query(query_partai_kompetisi_event))
    for row in list_partai_kompetisi_event:
        row[5] = row[5].strftime("%d %B %Y")
        row[6] = row[6].strftime("%d %B %Y")
        row[8] = False if (row[7] < 8) else True
        row[7] = f"{row[7]}/8"

    context = {
        'list_partai_kompetisi_event':list_partai_kompetisi_event
    }
    return render(request, 'partai_kompetisi_event_umpire.html', context)

def hasil_pertandingan(request, jenis_partai:str, nama_event:str, tahun_event:int):
    first, second, third, fourth, perempat_final = None,None,None,None,[]
    #### HELPER FUNCTION ####
    def isNotEqual(row, isSingle=True):
        flag = True
        first_to_fourth = [first, second, third, fourth]
        for bef_obj in first_to_fourth:
            if (bef_obj is not None):
                if (isSingle):
                    flag = flag and (row[:2] != bef_obj[:2])
                else:
                    flag = flag and (row[0] != bef_obj[0]) and (set(row[1].split(", ")) != set(bef_obj[1].split(", ")))
        return flag
    
    def seperatePerBabak(babak:str, ori_list):
        temp = []
        for row in ori_list:
            if (row[-1] == babak):
                temp.append(row)
        return temp
    
    ######### SINGLE #########
    if (jenis_partai.strip().endswith("S")):
        query_all_match_s = f'''
        SELECT 
            PMM.nomor_peserta, M.nama, PMM.status_menang, PMM.jenis_babak
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        query_all_match_s = list_tup_to_list_list(execute_query(query_all_match_s))
        ############### FINAL ###############
        list_final_s = seperatePerBabak('Final', query_all_match_s)[:2]
        for row in list_final_s:
            first = row if (row[2]) else None
            second = row if (not row[2]) else None
        ############### SEMIFINAL ###############
        list_semi_s = seperatePerBabak('Semifinal', query_all_match_s)[:4]
        for row in list_semi_s:
            third = row if (not row[2]) else None
            fourth = row if ((third is not None) and (not row[2])) else None
        ############### PEREMPAT ###############
        list_16besar_s = seperatePerBabak('16 Besar', query_all_match_s)[:16]
        for row in list_16besar_s:
            if ((row[2]) and isNotEqual(row)):
                perempat_final.append(row)
        
        ###### test ######
        print(f"first: {first}")
        print(f"second: {second}") 
        print(f"third: {third}") 
        print(f"fourth: {fourth}")
        print(f"perempat_final: {perempat_final}")
        print(f">> list: {list_final_s}")

    ######### DOUBLE #########
    else:
        query_all_match_d = f'''
        SELECT DISTINCT
            PeK.nomor_peserta, '' AS nama, PMM.status_menang, PMM.jenis_babak
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_all_match_d = list_tup_to_list_list(execute_query(query_all_match_d))
        for row in list_all_match_d:
            query_find_partner = f'''
            SELECT 
                STRING_AGG(m.nama,', ')
            FROM 
                peserta_kompetisi PeK 
                INNER JOIN member M ON (M.id = PeK.id_atlet_kualifikasi)
            WHERE 
                PeK.id_atlet_ganda IN (
                  SELECT PeK_sub.id_atlet_ganda FROM peserta_kompetisi PeK_sub
                  WHERE PeK_sub.nomor_peserta = {row[0]});
            '''
            row[1] = list_tup_to_list_list(execute_query(query_find_partner))[0][0]
        ####### FINAL #######
        list_final_d = seperatePerBabak('Final', list_all_match_d)[:2]
        for row in list_final_d:
            first = row if (row[2]) else None
            second = row if (not row[2]) else None
        ####### SEMIFINAL #######
        list_semi_d = seperatePerBabak('Semifinal', list_all_match_d)[:4]
        for row in list_semi_d:
            third = row if (not row[2]) else None
            fourth = row if ((third is not None) and (not row[2])) else None 
        ####### PEREMPAT #######
        list_16besar_d = seperatePerBabak('16 Besar', list_all_match_d)[:16]
        for row in list_16besar_d:
            if ((row[2]) and isNotEqual(row, isSingle=False)):
                perempat_final.append(row)

        ###### test ######
        print(f"first: {first}")
        print(f"second: {second}") 
        print(f"third: {third}") 
        print(f"fourth: {fourth}")
        print(f"perempat_final: {perempat_final}")
        print(f">> list: {list_final_d}")

    query_partai_kompetisi_event = f'''
    SELECT 
        E.nama_event, S.nama AS stadium, E.total_hadiah, E.kategori_superseries, 
        E.tgl_mulai, E.tgl_selesai, count(PPK.nomor_peserta) as kapasitas, PaK.jenis_partai
    FROM 
        partai_kompetisi PaK 
        INNER JOIN event E ON (PaK.nama_event = E.nama_event AND PaK.tahun_event = E.tahun)
        INNER JOIN stadium S ON (E.nama_stadium = S.nama)
        LEFT OUTER JOIN partai_peserta_kompetisi PPK ON (PPK.jenis_partai = PaK.jenis_partai AND PPK.nama_event = PaK.nama_event AND PPK.tahun_event = PaK.tahun_event)
    WHERE
        (PaK.jenis_partai = '{jenis_partai}' AND PaK.nama_event = '{nama_event}' AND PaK.tahun_event = {tahun_event})    
    GROUP BY 
        E.nama_event, stadium, E.total_hadiah, E.kategori_superseries, 
        E.tgl_mulai, E.tgl_selesai, kapasitas, PaK.jenis_partai;
    '''
    list_partai_kompetisi_event = list_tup_to_list_list(execute_query(query_partai_kompetisi_event))[:1]
    for row in list_partai_kompetisi_event:
        row[4] = row[4].strftime("%d %B %Y")
        row[5] = row[5].strftime("%d %B %Y")
        row[6] = f"{row[6]}/8"

    context = {
        'first':first,
        'second':second,
        'third':third,
        'fourth':fourth,
        'perempat_final':perempat_final,
        'card_partai_event':list_partai_kompetisi_event[0],
        'len_perempat':len(perempat_final)
    }
    return render(request, 'hasil_pertandingan_umpire.html', context)