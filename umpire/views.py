from django.shortcuts import render

# Create your views here.
def show_event(request):
    return render(request, 'list_event.html')

def show_result(request):
    return render(request, 'hasil_pertandingan.html')

def show_data_result(request):
    #print( request.session["id"])
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