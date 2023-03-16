from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader


def index(response):
    return HttpResponse("This message is from Restoring App")

def landing(request):
    # template = loader.get_template('')
    return render(request, 'landing.html', {})
