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
    # temp_dir = tempfile.mkdtemp()  # Create a temporary directory for the user
    request.session['user_id'] = user_id  # Store the user ID in the session
    # request.session['temp_dir'] = temp_dir  # Store the path to the temporary directory in the session
    return render(request, 'landing.html', {'user_id': user_id, 'protocol': protocol, 'host': host, 'port': port})

# def protected_view(request):
#     user_id = request.session.get('user_id')  # Retrieve the user ID from the session
#     temp_dir = request.session.get('temp_dir')  # Retrieve the path to the temporary directory from the session
#     if user_id:
#         # Your protected view code here
#         return JsonResponse({'message': 'Hello, user {}!'.format(user_id), 'temp_dir': temp_dir})
#     else:
#         return JsonResponse({'error': 'User ID not found'}, status=401)