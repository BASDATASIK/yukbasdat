from django.shortcuts import render
from django.shortcuts import redirect
from utils.query import *
from authentication.views import is_authenticated

# Create your views here.
def form_data_kualifikasi(request):
    return render(request, 'form_data_kualifikasi.html')

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
                print(result)
                return render(request, 'pertanyaan_kualifikasi.html', {'msg': 'Gagal menginput data'})
            else:
                return redirect('atlet:show_riwayat_ujian')
            
    return render(request, 'pertanyaan_kualifikasi.html', {'msg': ''})

def daftar_event1(request):
    return render(request, 'daftar_event1.html')

def daftar_event2(request):
    return render(request, 'daftar_event2.html')

def pilih_kategori(request):
    return render(request, 'pilih_kategori.html')

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