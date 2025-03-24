from django.shortcuts import render
from .models import Client
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def all_clients(request):
    user = request.user

    if user.user_type in ['admin', 'sales_manager']:
        clients= Client.objects.all()

    return render(request, 'all_clients.html', {'clients': clients})

   

