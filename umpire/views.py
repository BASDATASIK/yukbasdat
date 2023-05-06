from django.shortcuts import render

# Create your views here.
def show_event(request):
    return render(request, 'list_event.html')

def show_result(request):
    return render(request, 'hasil_pertandingan.html')

def show_data_result(request):
    return render(request, 'data_hasil_pertandingan.html')