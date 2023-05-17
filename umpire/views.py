from django.shortcuts import render
from utils.query import *

# Create your views here.
def show_event(request):
    return render(request, 'list_event.html')

def show_result(request):
    return render(request, 'hasil_pertandingan.html')

def show_data_result(request):
    return render(request, 'data_hasil_pertandingan.html')

def pertandingan_semifinal(request):
    return render(request, 'pertandingan_semifinal.html')

def pertandingan_final(request):
    return render(request, 'pertandingan_final.html')

def data_perolehan_poin(request):
    return render(request, 'data_perolehan_poin.html')

def pertandingan_perempatfinal(request):
    return render(request, 'pertandingan_perempatfinal.html')

def pertandingan_perebutan_juara_3(request):
    return render(request, 'pertandingan_perebutan_juara_3.html')

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
    
    ######### SINGLE #########
    if (jenis_partai.strip().endswith("S")):
        ############### FINAL ###############
        query_final_s = f'''
        SELECT 
            PMM.nomor_peserta, M.nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = 'Final' AND (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_final_s = list_tup_to_list_list(execute_query(query_final_s))[:2]
        for row in list_final_s:
            first = row if (row[2]) else None
            second = row if (not row[2]) else None
        ############### SEMIFINAL ###############
        query_semi_s = f'''
        SELECT 
            PMM.nomor_peserta, M.nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = 'Semifinal' AND (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_semi_s = list_tup_to_list_list(execute_query(query_semi_s))[:4]
        for row in list_semi_s:
            third = row if (not row[2]) else None
            fourth = row if ((third is not None) and (not row[2])) else None 
        ############### PEREMPAT ###############
        query_16besar_s = f'''
        SELECT 
            PMM.nomor_peserta, M.nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = '16 Besar' AND (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        query_16besar_s = list_tup_to_list_list(execute_query(query_16besar_s))[:16]
        for row in query_16besar_s:
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
        ####### FINAL #######
        query_final_d = f'''
        SELECT DISTINCT
            PeK.nomor_peserta, '' AS nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = 'Final' AND
            (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_final_d = list_tup_to_list_list(execute_query(query_final_d))[:2]
        for row in list_final_d:
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
            first = row if (row[2]) else None
            second = row if (not row[2]) else None
        ####### SEMIFINAL #######
        query_semi_d = f'''
        SELECT DISTINCT
            PeK.nomor_peserta, '' AS nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = 'Semifinal' AND
            (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_semi_d = list_tup_to_list_list(execute_query(query_semi_d))[:4]
        for row in list_semi_d:
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
            third = row if (not row[2]) else None
            fourth = row if ((third is not None) and (not row[2])) else None 
        ####### PEREMPAT #######
        query_16besar_d = f'''
        SELECT DISTINCT
            PeK.nomor_peserta, '' AS nama, PMM.status_menang
        FROM 
            partai_kompetisi PK 
            INNER JOIN partai_peserta_kompetisi PPK ON 
                (PK.jenis_partai = PPK.jenis_partai AND PK.nama_event = PPK.nama_event AND PK.tahun_event = PK.tahun_event)
            INNER JOIN peserta_mengikuti_match PMM ON (PMM.nomor_peserta = PPK.nomor_peserta)
            INNER JOIN peserta_kompetisi PeK ON (PeK.nomor_peserta = PMM.nomor_peserta)
            INNER JOIN member m on (PeK.id_atlet_kualifikasi = M.id)
        WHERE 
            PMM.jenis_babak = '16 Besar' AND
            (PK.jenis_partai = '{jenis_partai}' AND PK.nama_event = '{nama_event}' AND PK.tahun_event = {tahun_event});
        '''
        list_16besar_d = list_tup_to_list_list(execute_query(query_16besar_d))[:16]
        for row in list_16besar_d:
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