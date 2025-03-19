
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

            # ✅ Assign Lead Source
            source_id = request.POST.get('source')
            if source_id:
                try:
                    lead.source = LeadSource.objects.get(id=source_id)  # Assign LeadSource
                except LeadSource.DoesNotExist:
                    messages.error(request, "Invalid source selected.")
                    return redirect('create_lead')

            lead.save()  # ✅ Save Lead before assigning ManyToMany field

            # ✅ Assign Multiple Users to `assigned_to`
            assigned_user_ids = request.POST.getlist('assigned_to')  # Get multiple selected users
            users = User.objects.filter(id__in=assigned_user_ids)  # Fetch users from DB
            lead.assigned_to.set(users)  # ✅ Assign multiple users

            messages.success(request, "Lead created successfully!")
            return redirect('all_leads')
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "There was an error creating the lead. Please check the form.")
    else:
        form = LeadForm()

    users = User.objects.all()  # Fetch all users for selection
    lead_sources = LeadSource.objects.all()  # Fetch LeadSource options

    return render(request, 'create_lead.html', {'form': form, 'users': users, 'lead_sources': lead_sources})

@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)  # Get the specific lead
    users = User.objects.filter(user_type__in=['Sales Manager', 'Sales Representative'])

    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)  # Bind form to the instance
        if form.is_valid():
            form.save()
            return redirect("lead_detail", lead_id=lead.id)
    else:
        form = LeadForm(instance=lead)  # Populate form with existing data
    context = {
        'form': form,
        'lead': lead,
        'users': users,  # Pass users to template excluding Admin
    }
    return render(request, "edit_lead.html", context)


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

@login_required
def edit_lead_source(request,source_id):
    source = get_object_or_404(LeadSource, id=source_id)
    if request.method == 'POST':
        form = LeadSourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            return redirect('lead_source')
    else:
        form = LeadSourceForm(instance=source)
    return render(request, 'edit_leadsource.html', {'form': form,'source':source})

@login_required
def delete_lead_source(request, source_id):
    source = get_object_or_404(LeadSource, id=source_id)
    source.delete()
    return redirect('lead_source')