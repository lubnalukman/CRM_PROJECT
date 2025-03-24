
from usersapp.views import custom_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead, LeadSource, User,Communication
from .forms import LeadForm,CommunicationForm
from django.core.paginator import Paginator
from .forms import LeadSourceForm
from clientsapp.models import Client
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model 

User = get_user_model()

@login_required
def all_leads(request):
    user = request.user

    if user.user_type in ['admin', 'sales_manager']:
        # Admin and Sales Managers can view all leads
        leads = Lead.objects.all()
    else:
        # Sales Representatives can only see assigned leads
        leads = Lead.objects.filter(assigned_to=user)

    return render(request, 'all_leads.html', {'leads': leads})

@login_required
def create_lead(request):
    if request.method == 'POST':
        lead_form = LeadForm(request.POST)
        communication_form=CommunicationForm(request.POST)

        if lead_form.is_valid() and communication_form.is_valid():
            lead = lead_form.save(commit=False)  # Don't save yet

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

            communication, created = Communication.objects.update_or_create(
                lead=lead,
                created_by=request.user,  # Ensure uniqueness per user
                defaults={
                    'interaction_type': communication_form.cleaned_data['interaction_type'],
                    'subject': communication_form.cleaned_data['subject'],
                    'notes': communication_form.cleaned_data['notes'],
                    'updated_by': request.user,  # Update user
                }
            )

            messages.success(request, "Lead and initial communication details created successfully!")
            return redirect('all_leads')
        else:
            print(" lead Form Errors:", lead_form.errors)
            print("Communication Form Errors:", communication_form.errors)

            messages.error(request, "There was an error creating the lead. Please check the form.")
    else:
        lead_form = LeadForm()
        communication_form = CommunicationForm()

    users = User.objects.all()  # Fetch all users for selection
    lead_sources = LeadSource.objects.all()  # Fetch LeadSource options

    return render(request, 'create_lead.html', {
        'lead_form': lead_form,
        'communication_form': communication_form,
        'users': users,
        'lead_sources': lead_sources
    })
   
@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id) 
    users=User.objects.filter(user_type__in=['sales_manager', 'sales_rep']) # Get the specific lead
 
  # Fetch the latest communication entry for this lead, if it exists
    communication = Communication.objects.filter(lead=lead).order_by('-timestamp').first()

    if request.method == "POST":
        lead_form = LeadForm(request.POST, instance=lead)
        communication_form = CommunicationForm(request.POST, request.FILES,instance=communication)

        if lead_form.is_valid():
            lead_form.save()

             # Check if lead is converted and Client doesn't already exist
            if lead.status == "converted" and not Client.objects.filter(email=lead.email).exists():
                Client.objects.create(
                    first_name=lead.first_name,
                    last_name=lead.last_name,
                    email=lead.email,
                    phone_number=lead.phone_number,
                    source=lead.source,
                    created_by=request.user  # Track which user converted the lead
                )
                 # Update the converted_at and converted_by fields
                lead.converted_at = timezone.now()  # Ensure you have 'timezone' imported
                lead.converted_by = request.user
                lead.save()

                messages.success(request, "Lead converted to client successfully!")


            # Always allow users to create or update communication
            if communication_form.is_valid():
                communication = communication_form.save(commit=False)
                communication.lead = lead  # Associate the communication with the lead
                if not communication.created_by:  # Ensure created_by is set only if it's empty
                    communication.created_by = request.user
                communication.updated_by = request.user 
                communication.save()

            return redirect("lead_detail", lead_id=lead.id)
    else:
        lead_form = LeadForm(instance=lead)  # Populate form with existing data
        communication_form = CommunicationForm(instance=communication)  # Empty communication form

    context = {
        'lead_form': lead_form,
        'communication_form': communication_form,
        'lead': lead,   
        'users':users
    }
    return render(request, "edit_lead.html", context)


@login_required
def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.delete()
    return redirect('admin_dashboard')

@login_required
def lead_detail(request, lead_id):
    # Fetch the lead or return a 404 error
    lead = get_object_or_404(Lead, id=lead_id)

    # Fetch related communications for this lead
    communications = Communication.objects.filter(lead=lead).order_by('-timestamp')

    return render(request, 'lead_detail.html', {
        'lead': lead,
        'communications': communications,
    })

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
    current_user = request.user

    if current_user.user_type in ['admin','sales_manager']:
        source = get_object_or_404(LeadSource, id=source_id)
        source.delete()
    return redirect('lead_source')

