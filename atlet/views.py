from django.shortcuts import render
from django.shortcuts import redirect
from utils.auth_util_validation import throw_to_home_if_unauthorized
from utils.query import *
from authentication.views import is_authenticated

# Create your views here.
def show_riwayat_ujian(request):
    query = f"SELECT * FROM atlet_nonkualifikasi_ujian_kualifikasi WHERE id_atlet = '{request.session['id']}';"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'riwayat_ujian.html', {'riwayat_ujian': result})

def pertanyaan_kualifikasi(request, tahun, batch, tempat, tanggal):
    if request.method == 'POST':
            jawaban = []
            for i in range(1, 6):
                jawaban.append(request.POST.get('question'+str(i)))
            jawaban_benar = ['Raket', 'Footwork', 'Deuce', 'Bulu burung', '30']

            if None in jawaban:
                return render(request, 'pertanyaan_kualifikasi.html', {'msg': 'Jawaban tidak boleh kosong'})

            score = sum([1 for x, y in zip(jawaban, jawaban_benar) if x == y])
            
            if not is_authenticated(request):
                return render(request, 'pertanyaan_kualifikasi.html', {'msg': 'Anda belum login'})  
            
            id = request.session['id']
            if score >= 4:
                query = f"INSERT INTO atlet_nonkualifikasi_ujian_kualifikasi VALUES ('{id}', '{tahun}', '{batch}', '{tempat}', '{tanggal}', true);"
            else:
                query = f"INSERT INTO atlet_nonkualifikasi_ujian_kualifikasi VALUES ('{id}', '{tahun}', '{batch}', '{tempat}', '{tanggal}', false);"
            error, result = try_except_query(query)
            if error:
                msg = 'Gagal menginput data'
                print(result)
                if 'is not present in table "atlet_non_kualifikasi"' in str(result):
                    msg = 'Anda sudah terkualifikasi sehingga tidak bisa mengikuti ujian kualifikasi lagi'

                if 'already exists.' in str(result):
                    msg = 'Anda sudah pernah mengikuti ujian kualifikasi ini'

                return render(request, 'pertanyaan_kualifikasi.html', {'msg': msg})
            else:
                return redirect('atlet:show_riwayat_ujian') 
            
    return render(request, 'pertanyaan_kualifikasi.html', {'msg': ''})

def daftar_stadium(request):
    query = f"select * from stadium;"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    print(request.session["id"])
    print(result)
    return render(request, 'daftar_stadium.html', {'list_stadium': result})

def daftar_event(request, stadium):
    query = f"SELECT * FROM event WHERE nama_stadium = '{stadium}' AND event.tgl_mulai > CURRENT_DATE;"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'daftar_event.html', {'list_event': result})

def enrolled_partai_kompetisi_event(request):
    user = request.session['id']
    query = f'''
    SELECT e.Nama_Event, e.Tahun, e.Nama_Stadium, pk.Jenis_Partai, e.Kategori_Superseries, e.Tgl_Mulai, e.Tgl_Selesai
    FROM EVENT e
    JOIN PARTAI_KOMPETISI pk ON e.Nama_Event = pk.Nama_Event AND e.Tahun = pk.Tahun_Event
    JOIN PARTAI_PESERTA_KOMPETISI ppk ON pk.Jenis_Partai = ppk.Jenis_Partai AND pk.Nama_Event = ppk.Nama_Event AND pk.Tahun_Event = ppk.Tahun_Event
    JOIN PESERTA_KOMPETISI p ON ppk.Nomor_Peserta = p.Nomor_Peserta
    JOIN ATLET_GANDA ag ON p.ID_Atlet_Ganda = ag.ID_Atlet_Ganda
    JOIN ATLET_KUALIFIKASI ak ON p.ID_Atlet_Kualifikasi = ak.ID_Atlet
    JOIN ATLET a ON ak.ID_Atlet = a.ID
    WHERE a.ID = '{user}'; 
    '''
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'enrolled_partai_kompetisi_event.html', {'enrolled_partai_kompetisi_event': result})

def enrolled_event(request):
    user = request.session['id']
    query = f'''
    SELECT e.Nama_Event, e.Tahun, e.Nama_Stadium, e.Kategori_Superseries, e.Tgl_Mulai, e.Tgl_Selesai, 
    FROM EVENT e
    JOIN PARTAI_KOMPETISI pk ON e.Nama_Event = pk.Nama_Event AND e.Tahun = pk.Tahun_Event
    JOIN PARTAI_PESERTA_KOMPETISI ppk ON pk.Jenis_Partai = ppk.Jenis_Partai AND pk.Nama_Event = ppk.Nama_Event AND pk.Tahun_Event = ppk.Tahun_Event
    JOIN PESERTA_KOMPETISI p ON ppk.Nomor_Peserta = p.Nomor_Peserta
    JOIN ATLET_GANDA ag ON p.ID_Atlet_Ganda = ag.ID_Atlet_Ganda
    JOIN ATLET_KUALIFIKASI ak ON p.ID_Atlet_Kualifikasi = ak.ID_Atlet
    JOIN ATLET a ON ak.ID_Atlet = a.ID
    WHERE a.ID = '{user}'; 
    '''
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'enrolled_event.html', {'enrolled_event': result})

def delete_partai_kompetisi_by_atlet_id(atlet_id):
    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Delete data from PARTAI_PESERTA_KOMPETISI table for the specified athlete ID
        delete_partai_peserta_query = """
            DELETE FROM PARTAI_PESERTA_KOMPETISI
            WHERE Nomor_Peserta IN (
                SELECT Nomor_Peserta
                FROM PESERTA_KOMPETISI
                WHERE ID_Atlet_Ganda IN (
                    SELECT ID_Atlet_Ganda
                    FROM ATLET_GANDA
                    WHERE ID_Atlet_Kualifikasi = %s
                )
            )
        """
        cursor.execute(delete_partai_peserta_query, (atlet_id,))

        # Delete data from PESERTA_KOMPETISI table for the specified athlete ID
        delete_peserta_kompetisi_query = """
            DELETE FROM PESERTA_KOMPETISI
            WHERE ID_Atlet_Ganda IN (
                SELECT ID_Atlet_Ganda
                FROM ATLET_GANDA
                WHERE ID_Atlet_Kualifikasi = %s
            )
        """
        cursor.execute(delete_peserta_kompetisi_query, (atlet_id,))

        # Commit the transaction and close the cursor
        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error) as error:
        # Handle any potential errors
        print("Error deleting partai kompetisi data for atlet:", error)

def enrolled_event_delete(request, jenis, nama_event, tahun):
    user = request.session['id']
    query = f'''
    SELECT e.Nama_Event, e.Tahun, e.Nama_Stadium, e.Kategori_Superseries, e.Tgl_Mulai, e.Tgl_Selesai, 
    FROM EVENT e
    JOIN PARTAI_KOMPETISI pk ON e.Nama_Event = pk.Nama_Event AND e.Tahun = pk.Tahun_Event
    JOIN PARTAI_PESERTA_KOMPETISI ppk ON pk.Jenis_Partai = ppk.Jenis_Partai AND pk.Nama_Event = ppk.Nama_Event AND pk.Tahun_Event = ppk.Tahun_Event
    JOIN PESERTA_KOMPETISI p ON ppk.Nomor_Peserta = p.Nomor_Peserta
    JOIN ATLET_GANDA ag ON p.ID_Atlet_Ganda = ag.ID_Atlet_Ganda
    JOIN ATLET_KUALIFIKASI ak ON p.ID_Atlet_Kualifikasi = ak.ID_Atlet
    JOIN ATLET a ON ak.ID_Atlet = a.ID
    WHERE a.ID = '{user}'; 
    '''
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'enrolled_event.html', {'enrolled_event': result})

def list_sponsor(request):
    user = request.session['id']
    query = f'''
    SELECT SPONSOR.Nama_Brand, ATLET_SPONSOR.Tgl_Mulai, ATLET_SPONSOR.Tgl_Selesai
    FROM ATLET
    INNER JOIN ATLET_SPONSOR ON ATLET.ID = ATLET_SPONSOR.ID_Atlet
    INNER JOIN SPONSOR ON ATLET_SPONSOR.ID_Sponsor = SPONSOR.ID
    WHERE ATLET.ID = '{user}'
    '''
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'list_sponsor.html', {'list_sponsor': result})

def pilih_kategori(request, nama_event, tahun):
    query = f"SELECT jenis_kelamin FROM atlet WHERE id = '{request.session['id']}';"
    error, jenis_kelamin = try_except_query(query)
    jenis_kelamin = jenis_kelamin[0][0]

    query = f"SELECT * FROM event join stadium s on event.nama_stadium = s.nama WHERE nama_event = '{nama_event}' AND tahun = {tahun};"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    result = result[0]

    query = '''
            SELECT distinct
            jenis_partai,
            nama_event,
            tahun_event,
            COALESCE((
            SELECT COUNT(*)
            FROM partai_peserta_kompetisi ppk
            WHERE ppk.jenis_partai = ppk2.jenis_partai
                AND ppk.nama_event = ppk2.nama_event
                AND ppk.tahun_event = ppk2.tahun_event
            GROUP BY jenis_partai, nama_event, tahun_event
            ), 0) as jumlah_peserta 
                from partai_kompetisi ppk2
            WHERE nama_event = '{nama_event}' AND tahun_event = {tahun};
            '''.format(nama_event=nama_event, tahun=tahun)
    error, list_partai_kompetisi = try_except_query(query)
    list_partai_kompetisi = list_tup_to_list_list(list_partai_kompetisi)

    query = f"select * from atlet_ganda join atlet on atlet.id = atlet_ganda.id_atlet_kualifikasi join member on member.id = atlet_ganda.id_atlet_kualifikasi join peserta_kompetisi pk on atlet_ganda.id_atlet_ganda = pk.id_atlet_ganda join partai_peserta_kompetisi ppk on pk.nomor_peserta = ppk.nomor_peserta where id_atlet_kualifikasi_2 is null and jenis_kelamin = {jenis_kelamin} and nama_event = '{nama_event}' and tahun_event = {tahun};"

    error, list_atlet_jenis_kelamin = try_except_query(query)
    list_atlet_jenis_kelamin = list_tup_to_list_list(list_atlet_jenis_kelamin)

    query = f"select * from atlet_ganda join atlet on atlet.id = atlet_ganda.id_atlet_kualifikasi join member on member.id = atlet_ganda.id_atlet_kualifikasi join peserta_kompetisi pk on atlet_ganda.id_atlet_ganda = pk.id_atlet_ganda join partai_peserta_kompetisi ppk on pk.nomor_peserta = ppk.nomor_peserta where id_atlet_kualifikasi_2 is null and nama_event = '{nama_event}' and tahun_event = {tahun};"

    error, list_atlet = try_except_query(query)
    list_atlet = list_tup_to_list_list(list_atlet)

    partai_kompetisi_dict = {'MS': 'Tunggal Putra', 'WS': 'Tunggal Putri', 'MD': 'Ganda Putra', 'WD': 'Ganda Putri',
                             'XD': 'Ganda Campuran'}

    for i in range(len(list_partai_kompetisi)):
        if list_partai_kompetisi[i][0] in partai_kompetisi_dict:
            list_partai_kompetisi[i][0] = partai_kompetisi_dict[list_partai_kompetisi[i][0]]

    query = f"SELECT jenis_kelamin FROM atlet WHERE id = '{request.session['id']}';"
    error, jenis_kelamin = try_except_query(query)
    jenis_kelamin = jenis_kelamin[0][0]
    if str(jenis_kelamin) == 'False': # Putri
        list_partai_kompetisi = [x for x in list_partai_kompetisi if x[0] != 'Tunggal Putra' and x[0] != 'Ganda Putra']
    else: # Putra
        list_partai_kompetisi = [x for x in list_partai_kompetisi if x[0] != 'Tunggal Putri' and x[0] != 'Ganda Putri']

    query = f"SELECT * FROM atlet_ganda where id_atlet_kualifikasi = '{request.session['id']}' or id_atlet_kualifikasi_2 = '{request.session['id']}';"
    error, atlet_ganda = try_except_query(query)
    atlet_ganda = list_tup_to_list_list(atlet_ganda)
    if len(atlet_ganda) > 0:
        is_atlet_ganda = True
    else:
        is_atlet_ganda = False

    query = f"select * from atlet_kualifikasi where id_atlet = '{request.session['id']}';"
    error, atlet_kualifikasi = try_except_query(query)
    atlet_kualifikasi = list_tup_to_list_list(atlet_kualifikasi)
    if len(atlet_kualifikasi) > 0:
        is_atlet_kualifikasi = True
    else:
        is_atlet_kualifikasi = False

    query = f"select * from peserta_kompetisi where id_atlet_kualifikasi = '{request.session['id']}';"
    error, peserta_kompetisi = try_except_query(query)
    peserta_kompetisi = list_tup_to_list_list(peserta_kompetisi)
    if len(peserta_kompetisi) > 0:
        is_peserta_kompetisi = True
    else:
        is_peserta_kompetisi = False
    
    context = {
        'event': result,
        'list_partai_kompetisi': list_partai_kompetisi,
        'is_atlet_ganda': is_atlet_ganda,
        'is_atlet_kualifikasi': is_atlet_kualifikasi,
        'is_peserta_kompetisi': is_peserta_kompetisi,
        'list_atlet_jenis_kelamin': list_atlet_jenis_kelamin,
        'list_atlet': list_atlet,
    }

    if request.method == 'POST':
        atlet_tunggal_putra = request.POST.get('Tunggal Putra')
        atlet_tunggal_putri = request.POST.get('Tunggal Putri')
        atlet_ganda_putra = request.POST.get('Ganda Putra')
        atlet_ganda_putri = request.POST.get('Ganda Putri')
        atlet_ganda_campuran = request.POST.get('Ganda Campuran')

        print(atlet_tunggal_putra, atlet_tunggal_putri, atlet_ganda_putra, atlet_ganda_putri, atlet_ganda_campuran)
        if atlet_ganda_putra is not None and  atlet_ganda_putra != "None":
            print('masuk1')
            if atlet_ganda_putra == "Pilih Atlet":
                query = f"insert into atlet_ganda values ('{request.session['id']}', '{request.session['id']}', NULL);"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                query =  'select max(nomor_peserta) from peserta_kompetisi;'
                error, max_nomor_peserta = try_except_query(query)
                max_nomor_peserta = max_nomor_peserta[0][0]
                if max_nomor_peserta is None:
                    max_nomor_peserta = 0
                max_nomor_peserta += 1
                query = f"select world_rank, world_tour_rank from atlet_kualifikasi where id_atlet = '{request.session['id']}';"
                error, world_rank = try_except_query(query)
                world_rank = list_tup_to_list_list(world_rank)
                world_rank_keseluruhan = world_rank[0][0]
                world_tour_rank = world_rank[0][1]
                query = f"insert into peserta_kompetisi values ('{max_nomor_peserta}', '{request.session['id']}', null, '{world_rank_keseluruhan}', '{world_tour_rank}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                query = f"insert into partai_peserta_kompetisi values ('MD', '{nama_event}', '{tahun}', '{max_nomor_peserta}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    if 'Total point peserta tidak mencukupi' in str(result):
                        msg = str(result).split('CONTEXT')[0]
                        
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
            
            else:
                id_pasangan = atlet_ganda_putra
                query = f"update atlet_ganda set id_atlet_kualifikasi_2 = '{request.session['id']}' where id_atlet_kualifikasi = '{id_pasangan}';"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
            
        elif atlet_ganda_putri is not None and  atlet_ganda_putri != "None":
            print('masuk2')
            if atlet_ganda_putri == "Pilih Atlet":
                query = f"insert into atlet_ganda values ('{request.session['id']}', '{request.session['id']}', NULL);"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query =  'select max(nomor_peserta) from peserta_kompetisi;'
                error, max_nomor_peserta = try_except_query(query)
                max_nomor_peserta = max_nomor_peserta[0][0]

                if max_nomor_peserta is None:
                    max_nomor_peserta = 0
                max_nomor_peserta += 1
                query = f"select world_rank, world_tour_rank from atlet_kualifikasi where id_atlet = '{request.session['id']}';"
                error, world_rank = try_except_query(query)
                world_rank = list_tup_to_list_list(world_rank)
                world_rank_keseluruhan = world_rank[0][0]
                world_tour_rank = world_rank[0][1]
                query = f"insert into peserta_kompetisi values ('{max_nomor_peserta}', '{request.session['id']}', null, '{world_rank_keseluruhan}', '{world_tour_rank}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query = f"insert into partai_peserta_kompetisi values ('WD', '{nama_event}', '{tahun}', '{max_nomor_peserta}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    if 'Total point peserta tidak mencukupi' in str(result):
                        msg = str(result).split('CONTEXT')[0]
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)

            else:
                id_pasangan = atlet_ganda_putri
                query = f'update atlet_ganda set id_atlet_kualifikasi_2 = {request.session["id"]} where id_atlet_kualifikasi = {id_pasangan};'
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
            
        elif atlet_ganda_campuran is not None and  atlet_ganda_campuran != "None":
            print('masuk3')
            if atlet_ganda_campuran == "Pilih Atlet":
                query = f"insert into atlet_ganda values ('{request.session['id']}', '{request.session['id']}', NULL);"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query =  'select max(nomor_peserta) from peserta_kompetisi;'
                error, max_nomor_peserta = try_except_query(query)
                max_nomor_peserta = max_nomor_peserta[0][0]
                if max_nomor_peserta is None:
                    max_nomor_peserta = 0
                max_nomor_peserta += 1
                query = f"select world_rank, world_tour_rank from atlet_kualifikasi where id_atlet = '{request.session['id']}';"
                error, world_rank = try_except_query(query)
                world_rank = list_tup_to_list_list(world_rank)
                world_rank_keseluruhan = world_rank[0][0]
                world_tour_rank = world_rank[0][1]
                query = f"insert into peserta_kompetisi values ('{max_nomor_peserta}', '{request.session['id']}', null, '{world_rank_keseluruhan}', '{world_tour_rank}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query = f"insert into partai_peserta_kompetisi values ('XD', '{nama_event}', '{tahun}', '{max_nomor_peserta}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    if 'Total point peserta tidak mencukupi' in str(result):
                        msg = str(result).split('CONTEXT')[0]
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)

            else:
                id_pasangan = atlet_ganda_campuran
                query = f'update atlet_ganda set id_atlet_kualifikasi_2 = {request.session["id"]} where id_atlet_kualifikasi = {id_pasangan};'
                error, result = try_except_query(query) 
                if error:
                    print(result)
                    msg = "Gagal memilih"
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                msg = "Berhasil memilih"
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
            
        else:
            if jenis_kelamin:
                    partai = 'MS'
            else:
                partai = 'WS'

            if not is_peserta_kompetisi:
                query =  'select max(nomor_peserta) from peserta_kompetisi;'
                error, max_nomor_peserta = try_except_query(query)
                max_nomor_peserta = max_nomor_peserta[0][0]
                if max_nomor_peserta is None:
                    max_nomor_peserta = 0
                max_nomor_peserta += 1

                query = f"select world_rank, world_tour_rank from atlet_kualifikasi where id_atlet = '{request.session['id']}';"
                error, world_rank = try_except_query(query)
                world_rank = list_tup_to_list_list(world_rank)
                world_rank_keseluruhan = world_rank[0][0]
                world_tour_rank = world_rank[0][1]

                query = f"insert into peserta_kompetisi values ('{max_nomor_peserta}', null, {request.session['id']}, '{world_rank_keseluruhan}', '{world_tour_rank}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = 'Gagal mendaftar kompetisi'
                    if 'already exists.' in str(result):
                        msg = 'Anda sudah terdaftar pada kompetisi ini'
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query = f"insert into partai_peserta_kompetisi values ('{partai}', '{nama_event}', '{tahun}', '{max_nomor_peserta}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = 'Gagal mendaftar kompetisi'
                    if 'already exists.' in str(result):
                        msg = 'Anda sudah terdaftar pada kompetisi ini'
                    if 'Total point peserta tidak mencukupi' in str(result):
                        msg = str(result).split('CONTEXT')[0]
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                
                msg = 'Berhasil mendaftar kompetisi'
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
            else:
                if atlet_ganda_putra is 'Pilih Atlet' or atlet_ganda_putri is 'Pilih Atlet' or atlet_ganda_campuran is 'Pilih Atlet':
                    msg = 'Gagal mendaftar kompetisi'
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                query = f"select nomor_peserta from peserta_kompetisi where id_atlet_kualifikasi = '{request.session['id']}';"
                error, nomor_peserta = try_except_query(query)
                nomor_peserta = list_tup_to_list_list(nomor_peserta)
                nomor_peserta = nomor_peserta[0][0]
                query = f"insert into partai_peserta_kompetisi values ('{partai}', '{nama_event}', '{tahun}', '{nomor_peserta}');"
                error, result = try_except_query(query)
                if error:
                    print(result)
                    msg = 'Gagal mendaftar kompetisi'
                    if 'already exists.' in str(result):
                        msg = 'Anda sudah terdaftar pada kompetisi ini'
                    if 'Total point peserta tidak mencukupi' in str(result):
                        msg = str(result).split('CONTEXT')[0]
                    context['msg'] = msg
                    return render(request, 'pilih_kategori.html', context)
                msg = 'Berhasil mendaftar kompetisi'
                context['msg'] = msg
                return render(request, 'pilih_kategori.html', context)
 
    return render(request, 'pilih_kategori.html', context)

def unenrolled_event(request):
    return render(request, 'unenrolled_event.html')

def daftar_sponsor(request):
    return render(request, 'daftar_sponsor.html')

def dashboard(request):
    if throw_to_home_if_unauthorized(request, "atlet"):
        return redirect("/")
    id_atlet = request.session.get("id")
    query_dashboard = f'''
    SELECT 
        m.nama, a.negara_asal, m.email, a.tgl_lahir, A.play_right, A.height, STRING_AGG(DISTINCT MP.nama, ', '), 
        CASE
            WHEN ANK.id_atlet IS NOT NULL THEN 'Non Kualifikasi'
            WHEN AK.id_atlet IS NOT NULL THEN 'Kualifikasi'
            ELSE ''
        END AS status, 
        CASE
            WHEN ANK.id_atlet IS NOT NULL THEN '-'
            WHEN AK.id_atlet IS NOT NULL THEN cast(AK.world_rank as varchar)
            ELSE ''
        END AS world_rank_show,
        COALESCE(SUM(PH.total_point),0) AS total_point_all_time
    FROM 
        atlet A 
        INNER JOIN member M ON (A.id = m.id)
        LEFT OUTER JOIN atlet_pelatih AP ON (AP.id_atlet = A.id)
        LEFT OUTER JOIN pelatih P ON (AP.id_pelatih = P.id)
        LEFT OUTER JOIN member MP ON (P.id = MP.id)
        LEFT OUTER JOIN atlet_non_kualifikasi ANK ON (A.id = ANK.id_atlet)
        LEFT OUTER JOIN atlet_kualifikasi AK ON (A.id = AK.id_atlet)
        LEFT OUTER JOIN point_history PH ON (PH.id_atlet = A.id)
    WHERE 
        A.id = '{id_atlet}'
    GROUP BY 
        m.nama, a.negara_asal, m.email, a.tgl_lahir, A.play_right, A.height, status, world_rank_show
    '''
    data_atlet = list_tup_to_list_list(execute_query(query_dashboard))[0]
    data_atlet[4] = 'Kanan' if data_atlet[4] else 'Kiri'
    return render(request, 'dashboard.html', context={'data_atlet':data_atlet})

def daftar_ujian(request):
    list_ujian = execute_query(
        '''
        SELECT * FROM ujian_kualifikasi;
        '''
    )
    list_ujian = list_tup_to_list_list(list_ujian)
    return render(request, 'list_ujian_kualifikasi.html', {'list_ujian': list_ujian})