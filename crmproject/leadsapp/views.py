
from usersapp.views import custom_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead, LeadSource, User
from .forms import LeadForm
from django.core.paginator import Paginator
from .forms import LeadSourceForm
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model 

User = get_user_model()

def check_user_access(request, user_type, template_name):
    """Checks if the user is authenticated and has the correct user type."""
    if not request.user.is_authenticated or request.user.user_type != user_type:
        return redirect('custom_login')
    return render(request, template_name)

def admin_dashboard(request):
    return check_user_access(request, 'admin', 'admin_dashboard.html')

def manager_dashboard(request):
    return check_user_access(request, 'sales_manager', 'salesmanager_dashboard.html')

def salesrep_dashboard(request):
    return check_user_access(request, 'sales_rep', 'salesrep_dashboard.html')

def viewer_dashboard(request):
    return check_user_access(request, 'viewer', 'viewer_dashboard.html')

@login_required
def admin_view(request):
    # Ensure the user is an admin
    if request.user.user_type != 'admin':
        return redirect('custom_login')
    
    leads = Lead.objects.all()
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'leads': leads, 'users': users})

@login_required
def all_leads(request):
    # Fetch all leads
    leads = Lead.objects.all()
    
    return render(request, 'all_leads.html', {'leads': leads})

@login_required
def create_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)  # Don't save yet

            source_id = request.POST.get('source')
            if source_id:
                try:
                    lead.sources = LeadSource.objects.get(id=source_id)  # Assign LeadSource object
                except LeadSource.DoesNotExist:
                    messages.error(request, "Invalid source selected.")
                    return redirect('create_lead')

            assigned_user_id = request.POST.get('assigned_to')
            if assigned_user_id:
                try:
                    lead.assigned_to = User.objects.get(id=assigned_user_id)  # Assign user
                except User.DoesNotExist:
                    messages.error(request, "Invalid assigned user.")
                    return redirect('create_lead')
            lead.save()  # Now save the lead
            messages.success(request, "Lead created successfully!")
            return redirect('all_leads')
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "There was an error creating the lead. Please check the form.")
    else:
        form = LeadForm()

    users = User.objects.all()  # Fetch all users for the dropdown
    lead_sources = LeadSource.objects.all()  # Fetch LeadSource options for dropdown

    return render(request, 'create_lead.html', {'form': form, 'users': users,'lead_sources': lead_sources })

@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('all_leads')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'edit_lead.html', {'form': form})

@login_required
def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.delete()
    return redirect('admin_dashboard')

@login_required
def lead_detail(request, lead_id):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('custom_login')
    
    # Fetch the lead or return a 404 error
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Render the lead detail template
    return render(request, 'lead_detail.html', {'lead': lead})

def lead_source_list(request):
    sources=LeadSource.objects.all()
    return render (request,"lead_sources.html",{"sources":sources})

def create_lead_source(request):
    if request.method == 'POST':
        form=LeadSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lead_source')
    else:
        form = LeadSourceForm
    return render(request, "create_lead_source.html", {"form": form})