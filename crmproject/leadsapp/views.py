from usersapp.views import custom_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead, LeadSource, User,Communication,Notification
from .forms import LeadForm,CommunicationForm
from django.core.paginator import Paginator
from .forms import LeadSourceForm
from clientsapp.models import Client
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model 
from django.core.mail import send_mail
from django.http import JsonResponse

User = get_user_model()

@login_required
def leads_list(request):
    user = request.user
    status_filter = request.GET.get('status')  # Get status filter from URL query parameters

    if user.user_type in ['admin', 'sales_manager']:
        leads = Lead.objects.all()  # Admin & Sales Managers see all leads
    else:
        leads = Lead.objects.filter(assigned_to=user)  # Sales Reps see only assigned leads

    if status_filter:  # Apply status filter if it exists
        leads = leads.filter(status=status_filter)

    return render(request, 'leads_list.html', {'leads': leads})

@login_required
def create_lead(request):
    if request.method == 'POST':
        lead_form = LeadForm(request.POST)

        if lead_form.is_valid():
            lead = lead_form.save(commit=False)  

            lead.source = lead_form.cleaned_data["source"]  
            lead.save() 

            #  Assign Multiple Users to `assigned_to`
            assigned_user_ids = request.POST.getlist('assigned_to')  # Get multiple selected users
            users = User.objects.filter(id__in=assigned_user_ids,user_type__in=['sales_rep', 'sales_manager'])  # Fetch users from DB
            lead.assigned_to.set(users)  # Assign multiple users

            #  Create a default communication entry
            if not Communication.objects.filter(lead=lead).exists():
                Communication.objects.create(
                    lead=lead,
                    created_by=request.user,  #  Track the user who created it
                    interaction_type="email",  # Ensure lowercase matches the model choices
                    subject="Initial Contact",
                    notes="Follow-up required."
                )
            notify_users(lead)
            messages.success(request, "Lead created successfully!")
            return redirect('leads_list')
        else:
            print(" lead Form Errors:", lead_form.errors)
            messages.error(request, "There was an error creating the lead. Please check the form.")
    else:
        lead_form = LeadForm()
       
    users = User.objects.filter(user_type__in=['sales_rep', 'sales_manager'])  # Fetch all users for selection
    lead_sources = LeadSource.objects.all()  # Fetch LeadSource options

    return render(request, 'create_lead.html', {'lead_form': lead_form,'users': users,'lead_sources': lead_sources})

@login_required
def edit_communication(request, lead_id, communication_id):
    lead = get_object_or_404(Lead, id=lead_id)
    communication = get_object_or_404(Communication, id=communication_id, lead=lead)

    if request.method == "POST":
        form = CommunicationForm(request.POST, request.FILES, instance=communication)
        if form.is_valid():
            form.save()
            return redirect('lead_detail', lead_id=lead.id)  # Redirect back to lead details page
    else:
        form = CommunicationForm(instance=communication)

    return render(request, 'edit_communication.html', {'form': form, 'lead': lead, 'communication': communication})

@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id) 
    users=User.objects.filter(user_type__in=['sales_manager', 'sales_rep']) # Get the specific lead
    assigned_users = set(lead.assigned_to.all()) 

    if request.method == "POST":
        lead_form = LeadForm(request.POST, instance=lead)
    
        if lead_form.is_valid():
            lead_form.save()

            new_assigned_users = set(lead.assigned_to.all()) - assigned_users
            # ✅ Notify newly assigned sales representatives
            for user in new_assigned_users:
                # System Notification
                Notification.objects.create(
                    user=user,
                    message=f"You have been assigned to lead: {lead.first_name} {lead.last_name}."
                )

                # Email Notification
                send_mail(
                    subject="New Lead Assignment",
                    message=f"You have been assigned to a lead: {lead.first_name} {lead.last_name}. Please follow up accordingly.",
                    from_email="dhibilu@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=True
                )

            if lead.status == "converted" and not Client.objects.filter(email=lead.email).exists(): # Check if lead is converted and Client doesn't already exist
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

            return redirect("lead_detail", lead_id=lead.id)
    else:
        lead_form = LeadForm(instance=lead)  # Populate form with existing data

    context = {
        'lead_form': lead_form,
        'lead': lead,   
        'users':users
    }
    return render(request, "edit_lead.html", context)


@login_required
def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.delete()
    return redirect('leads_list')

@login_required
def lead_detail(request, lead_id):
    # Fetch the lead and communication or return a 404 error
    lead = get_object_or_404(Lead, id=lead_id)
    communications = Communication.objects.filter(lead=lead).order_by('-timestamp')
    communication_form = CommunicationForm()

    return render(request, 'lead_detail.html', {
        'lead': lead,
        'communications': communications,
        'communication_form': communication_form,
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

def notify_users(lead): 
    admin_users = User.objects.filter(user_type__in=['admin', 'sales_manager'])
    
    for user in admin_users:
        Notification.objects.create(
            user=user,
            message=f"New lead added: {lead.first_name} {lead.last_name} from {lead.source.source}."
        )

        send_mail(
            subject="New Lead Notification",
            message=f"A new lead '{lead.first_name} {lead.last_name}' has been added from {lead.source.source}.",
            from_email="dhibilu@gmail.com",
            recipient_list=[user.email],
            fail_silently=True
        )

    assigned_users = lead.assigned_to.all()
    
    for user in assigned_users:
        Notification.objects.create(
            user=user,
            message=f"You have been assigned a new lead: {lead.first_name} {lead.last_name}."
        )
        send_mail(
            subject="Lead Assignment Notification",
            message=f"You have been assigned a new lead: '{lead.first_name} {lead.last_name}'. Please follow up accordingly.",
            from_email="dhibilu@gmail.com",
            recipient_list=[user.email],
            fail_silently=True
        )

def mark_notifications_read(request):
    if request.user.is_authenticated:
        # Mark all unread notifications as read
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        
        # Get the updated unread notification count
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({"success": True, "unread_count": unread_count})
    
    return JsonResponse({"success": False})