
from usersapp.views import custom_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead, LeadSource, User
from .forms import LeadForm
from django.core.paginator import Paginator


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
    paginator = Paginator(leads, 10)  # Show 10 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'all_leads.html', {'page_obj': page_obj})

@login_required
def create_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = LeadForm()
    return render(request, 'create_lead.html', {'form': form})

@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
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

