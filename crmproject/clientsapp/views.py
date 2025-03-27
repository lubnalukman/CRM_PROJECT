from django.shortcuts import render,redirect,get_object_or_404
from .models import Client
from django.contrib.auth.decorators import login_required
from .forms import ClientForm
from leadsapp.models import Lead, LeadSource
from django.contrib import messages
from django.utils import timezone
# Create your views here.

@login_required
def clients_list(request):

    if request.user.user_type in['admin','sales_manager']:
        clients = Client.objects.all()  # Admin & Sales Managers see all clients
    elif request.user.user_type == 'sales_rep':
        clients = Client.objects.filter(created_by=request.user)  # Sales Reps see only their clients
    else:
        clients = Client.objects.none()  # Restrict access for other roles

    return render(request, 'clients_list.html', {'clients': clients})

@login_required
def create_client(request):
    if request.method =='POST':
        form=ClientForm(request.POST)
        if form.is_valid():
            client=form.save(commit=False)
            source_id = request.POST.get('source')
            if source_id:
                try:
                    client.source = LeadSource.objects.get(id=source_id)  # Assign LeadSource
                except LeadSource.DoesNotExist:
                    messages.error(request, "Invalid source selected.")
                    return redirect('create_client')
                
            client.created_by = request.user 
            client.save()
            return redirect('clients_list')
    else:
        form=ClientForm

    lead_sources = LeadSource.objects.all()
    return render(request,"create_client.html",{"form":form,'lead_sources':lead_sources})

@login_required
def client_details(request, client_id):
    current_user = request.user

    # Admins can view all users
    if current_user.user_type == 'admin':
        client = get_object_or_404(Client, id=client_id)
    else:
        # Sales Managers can only view Sales Representatives
        client = get_object_or_404(Client, id=client_id, user_type='sales_rep')

    return render(request, 'client_details.html', {'client': client})

@login_required
def edit_client(request, client_id):
    current_user = request.user

    # Restrict access based on user type
    if current_user.user_type == 'admin':
        client = get_object_or_404(Client, id=client_id)
    else:
        client = get_object_or_404(Client, id=client_id, created_by=request.user)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client details updated successfully!")
            return redirect('clients_list')
        else:
            messages.error(request, "Error updating client. Please check the form.")  # Debugging

    else:
        form = ClientForm(instance=client)

    return render(request, 'edit_client.html', {'form': form})

@login_required
def delete_lead(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return redirect('clients_list')
