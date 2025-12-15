from django.shortcuts import render
from .models import Webcam

def index(request):
    return render(request, "webcams/index.html", {"webcams": Webcam.objects.all()})
