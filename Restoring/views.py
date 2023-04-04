from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import uuid
from django.conf import settings
import tempfile



def index(response):
    return HttpResponse("This message is from Restoring App")

def landing(request):
    user_id = str(uuid.uuid4())[:8]  # Generate a unique user ID
    protocol = settings.PROTOCOL
    host = settings.HOST
    port = settings.PORT
    GA_MEASUREMENT_ID = settings.GA_MEASUREMENT_ID
    print(f'GA_MEASUREMENT_ID_VIEWS: {GA_MEASUREMENT_ID}')
    request.session['user_id'] = user_id  # Store the user ID in the session
    # request.session['temp_dir'] = temp_dir  # Store the path to the temporary directory in the session
    return render(request, 'landing.html', {'user_id': user_id, 'protocol': protocol, 'host': host, 'port': port, 'GA_MEASUREMENT_ID': GA_MEASUREMENT_ID})
