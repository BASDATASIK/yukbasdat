from django.shortcuts import render
from django.shortcuts import redirect
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
    return render(request, 'daftar_stadium.html', {'list_stadium': result})

def daftar_event(request, stadium):
    query = f"SELECT * FROM event WHERE nama_stadium = '{stadium}' AND event.tgl_mulai > CURRENT_DATE;"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    return render(request, 'daftar_event.html', {'list_event': result})

def pilih_kategori(request, nama_event, tahun):
    query = f"SELECT * FROM event join stadium s on event.nama_stadium = s.nama WHERE nama_event = '{nama_event}' AND tahun = {tahun};"
    error, result = try_except_query(query)
    result = list_tup_to_list_list(result)
    result = result[0]

    query = '''
            SELECT
            jenis_partai,
            nama_event,
            tahun_event,
            (SELECT count(*) FROM partai_peserta_kompetisi ppk
                            WHERE ppk.jenis_partai = ppk2.jenis_partai AND
                                ppk.nama_event = ppk2.nama_event AND
                                ppk.tahun_event = ppk2.tahun_event
                            GROUP BY jenis_partai, nama_event, tahun_event
            ) as jumlah_peserta
            from partai_peserta_kompetisi ppk2
            WHERE nama_event = '{nama_event}' AND tahun_event = {tahun};
            '''.format(nama_event=nama_event, tahun=tahun)
    error, list_partai_kompetisi = try_except_query(query)
    list_partai_kompetisi = list_tup_to_list_list(list_partai_kompetisi)

    query = f"SELECT jenis_kelamin FROM atlet WHERE id = '{request.session['id']}';"
    error, jenis_kelamin = try_except_query(query)
    jenis_kelamin = jenis_kelamin[0][0]

    query = f"select * from atlet_ganda join atlet on atlet.id = atlet_ganda.id_atlet_kualifikasi join member on member.id = atlet_ganda.id_atlet_kualifikasi join peserta_kompetisi pk on atlet_ganda.id_atlet_ganda = pk.id_atlet_ganda join partai_peserta_kompetisi ppk on pk.nomor_peserta = ppk.nomor_peserta where id_atlet_kualifikasi_2 is null and jenis_kelamin = {jenis_kelamin};"

    error, list_atlet_jenis_kelamin = try_except_query(query)
    list_atlet_jenis_kelamin = list_tup_to_list_list(list_atlet_jenis_kelamin)

    query = f"select * from atlet_ganda join atlet on atlet.id = atlet_ganda.id_atlet_kualifikasi join member on member.id = atlet_ganda.id_atlet_kualifikasi join peserta_kompetisi pk on atlet_ganda.id_atlet_ganda = pk.id_atlet_ganda join partai_peserta_kompetisi ppk on pk.nomor_peserta = ppk.nomor_peserta where id_atlet_kualifikasi_2 is null;"

    error, list_atlet = try_except_query(query)
    list_atlet = list_tup_to_list_list(list_atlet)

    for i in range(len(list_partai_kompetisi)):
        if list_partai_kompetisi[i][0] == 'MS':
            list_partai_kompetisi[i][0] = 'Tunggal Putra'
        elif list_partai_kompetisi[i][0] == 'WS':
            list_partai_kompetisi[i][0] = 'Tunggal Putri'
        elif list_partai_kompetisi[i][0] == 'MD':
            list_partai_kompetisi[i][0] = 'Ganda Putra'
        elif list_partai_kompetisi[i][0] == 'WD':
            list_partai_kompetisi[i][0] = 'Ganda Putri'
        elif list_partai_kompetisi[i][0] == 'XD':
            list_partai_kompetisi[i][0] = 'Ganda Campuran'

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
    return render(request, 'pilih_kategori.html', context)

def unenrolled_event(request):
    return render(request, 'unenrolled_event.html')

def daftar_sponsor(request):
    return render(request, 'daftar_sponsor.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def daftar_ujian(request):
    list_ujian = execute_query(
        '''
        SELECT * FROM ujian_kualifikasi;
        '''
    )
    list_ujian = list_tup_to_list_list(list_ujian)
    return render(request, 'list_ujian_kualifikasi.html', {'list_ujian': list_ujian})