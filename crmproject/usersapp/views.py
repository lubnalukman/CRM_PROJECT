from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail
from .forms import SignupForm
from leadsapp.models import Lead, LeadSource,Notification
from django.contrib.auth.decorators import login_required
from usersapp.forms import UserForm,UserProfileForm, UserEditForm
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model 
from django.contrib.auth.forms import AuthenticationForm
import logging
from clientsapp.models import Client
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


def index(request):
    return render(request,"index.html")

User = get_user_model()

def signup_user(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create and save the user
            user = form.save(commit=False)
            user.user_type = 'viewer'  # Assign default user type
            user.save()
            send_verification_email(request, user)
            messages.success(request, "Signup successful! Please check you email to verify your account.")
            return redirect('custom_login')  # Redirect to login page
        else:
            # Print errors in the console
            print("Form Errors:", form.errors)

            # Show errors on the page
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if not user.is_verified:
                     return render(request, 'registration/login.html', {
                        'form': form,
                        'error_message': 'Please verify your email before logging in.'
                    })
                login(request, user)
                # Redirect based on user type
                if user.user_type == 'admin':
                    return redirect('admin_dashboard')
                elif user.user_type == 'sales_manager':
                    return redirect('manager_dashboard')
                elif user.user_type == 'sales_rep':
                    return redirect('salesrep_dashboard')
                else:
                    # Default redirect if usertype doesn't match any case
                    return redirect('viewer_dashboard') 
            else:
                # Return an 'invalid login' error message
                return render(request, 'registration/login.html', {
                    'form': form,
                    'error_message': 'Invalid username or password'
                })
        else:
            # Form is invalid
            return render(request, 'registration/login.html', {
                'form': form,
                'error_message': 'Invalid form submission'
            })
    else:
        # GET request - show empty login form
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    subject = 'Verify your email - CRM'
    message = f"Hi {user.username},\n\nClick the link below to verify your email:\n{verification_link}"
    from_email = 'noreply@yourcrm.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, "✅ Your email has been verified. Please log in.")
        return redirect('custom_login')  # Redirect to login with success message
    else:
        messages.error(request, "❌ Verification link is invalid or expired.")
    return redirect('custom_login')

@login_required
def user_profile(request):
    user = request.user  # Get the logged-in user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    else:
        form = UserProfileForm(instance=user)  

    return render(request, 'user_profile.html', {'form': form})

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        return redirect('custom_login')  # Or some unauthorized page

    # Fetch latest  clients and leads
    recent_clients = Client.objects.order_by('-created_at')[:2]
    recent_leads = Lead.objects.order_by('-created_at')[:2]
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    # Count statistics
    total_clients = Client.objects.count()
    total_leads = Lead.objects.count()
    total_users = User.objects.count()  # Total registered users
    interested_leads = Lead.objects.filter(status='interested').count()  # Assuming 'status' field

    context = {
        'recent_clients': recent_clients,
        'recent_leads': recent_leads,
        'total_clients': total_clients,
        'total_leads': total_leads,
        'total_users': total_users,
        'interested_leads': interested_leads,
        'notifications': notifications
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def manager_dashboard(request):
    if request.user.user_type != 'sales_manager':
        return redirect('custom_login')  # Redirect if not a Sales Manager
   
    recent_clients = Client.objects.order_by('-created_at')[:2]
    recent_leads = Lead.objects.order_by('-created_at')[:2]
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    # Count statistics
    total_clients = Client.objects.count()
    total_leads = Lead.objects.count()
    total_users = User.objects.count()  # Total registered users
    interested_leads = Lead.objects.filter(status='interested').count()  # Assuming 'status' field

    context = {
        'recent_clients': recent_clients,
        'recent_leads': recent_leads,
        'total_clients': total_clients,
        'total_leads': total_leads,
        'total_users': total_users,
        'interested_leads': interested_leads,
        'notifications': notifications
    }
    
    return render(request, 'salesmanager_dashboard.html', context)
   

@login_required
def salesrep_dashboard(request):
    if request.user.user_type != 'sales_rep':
        return redirect('custom_login')

    # Fetch clients created by the logged-in sales rep
    recent_clients = Client.objects.filter(created_by=request.user).order_by('-created_at')[:1]

    # Fetch leads assigned to the sales rep, but only if the related client was created by them
    recent_leads = Lead.objects.filter(assigned_to=request.user).order_by('-created_at')[:1]
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    # Count statistics (only for their assigned leads and created clients)
    total_clients = Client.objects.filter(created_by=request.user).count()
    total_leads = Lead.objects.filter(assigned_to=request.user).count()
    interested_leads = Lead.objects.filter(assigned_to=request.user,status='interested').count()

    context = {
        'recent_clients': recent_clients,
        'recent_leads': recent_leads,
        'total_clients': total_clients,
        'total_leads': total_leads,
        'interested_leads': interested_leads,
        'notifications': notifications
    }

    return render(request, 'salesrep_dashboard.html', context)
   

@login_required
def viewer_dashboard(request):
    if request.user.user_type != 'viewer':
        return redirect('custom_login')
    return render(request, 'viewer_dashboard.html')


@login_required
def users_list(request):
    current_user = request.user

    # Determine which users to show based on user type
    if current_user.user_type == "admin":
        users = User.objects.all()
    elif current_user.user_type == "sales_manager":
        users = User.objects.filter(user_type="sales_rep")
    else:
        users = User.objects.none()  # No users visible to Sales Reps or other roles

    # Paginate the results
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    return render(request, 'users_list.html', {'page_obj': page_obj})

@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        password1 = request.POST.get('password1')  # Get the first password
        password2 = request.POST.get('password2')  # Get the second password (confirmation)

        if password1 != password2:
            form.add_error('password', 'Passwords do not match.')  # Add error if passwords do not match
        elif form.is_valid():
            user = form.save(commit=False)
            user.set_password(password1)  # Set the password
            user.save()  # Save the user object
            return redirect('users_list')
    else:
        form = UserForm()
    
    return render(request, 'create_user.html', {'form': form})


@login_required
def edit_user(request, user_id):
    current_user = request.user

    # Restrict access based on user type
    if current_user.user_type == 'admin':
        user = get_object_or_404(User, id=user_id)
    else:
        user = get_object_or_404(User, id=user_id, user_type='sales_rep')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users_list')
        else:
            print(form.errors)  # Debugging
    else:
        form = UserEditForm(instance=user)

    return render(request, 'edit_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    current_user = request.user

    # Admin can delete any user
    if current_user.user_type == 'admin':
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully.")
    
    # Sales Manager can only delete Sales Representatives (Optional)
    else:
        user = get_object_or_404(User, id=user_id, user_type='sales_rep')
        user.delete()
        messages.success(request, "Sales Representative deleted successfully.")

    return redirect('users_list')

@login_required
def user_detail(request, user_id):
    current_user = request.user

    # Admins can view all users
    if current_user.user_type == 'admin':
        user = get_object_or_404(User, id=user_id)
    else:
        # Sales Managers can only view Sales Representatives
        user = get_object_or_404(User, id=user_id, user_type='sales_rep')

    return render(request, 'user_detail.html', {'user': user})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('index')  # Redirect to the login page or any other page

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            # Get the user's email from the session
            email = request.session.get('email')
            user = User.objects.get(email=email)
            # Set the new password
            user.set_password(new_password)
            user.save()
            # Update the session to keep the user logged in
            update_session_auth_hash(request, user)
            # Clear the OTP and email from the session
            del request.session['otp']
            del request.session['email']
            messages.success(request, 'Your password has been successfully reset.')
            return redirect('custom_login')
        else:
            # Passwords do not match
            messages.error(request, 'Passwords do not match. Please try again.')
            return redirect('reset_password')
    return render(request, 'registration/reset_password.html')

def generate_otp():
    # Generate a random 6-digit OTP
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def request_otp(request):
    if request.method == 'POST':
        email = request.POST['email']
        # Generate OTP
        otp = generate_otp()
        # Send OTP to the user's email
        send_otp_email(email, otp)
        # Store OTP in the session
        request.session['otp'] = otp
        request.session['email'] = email
        messages.success(request, 'OTP has been sent to your email. Please check your inbox.')
        return redirect('verify_otp')
    return render(request, 'registration/request_otp.html')

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST['otp']
        stored_otp = request.session.get('otp')
        if user_otp == stored_otp:
            # OTP is valid, allow password reset
            messages.success(request, 'OTP verified. You can now reset your password.')
            return redirect('reset_password')
        else:
            # OTP is invalid
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
    return render(request, 'registration/verify_otp.html')

def search(request): 
    query = request.GET.get('q', '')
    user = request.user

    # Default empty querysets
    leads = Lead.objects.none()
    users = User.objects.none()
    clients = Client.objects.none()

    if user.user_type == 'Sales Representative':
        leads = Lead.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query),
            assigned_to=user
        )

        clients = Client.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query),
            Q(assigned_to=user) | Q(created_by=user)
        )

    elif user.user_type == 'Sales Manager':
        leads = Lead.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        clients = Client.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        users = User.objects.filter(
            Q(username__icontains=query),
            user_type='Sales Representative'
        )

    else:  # For Admin or others
        leads = Lead.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        clients = Client.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        users = User.objects.filter(
            Q(username__icontains=query)
        )

    result_data = {
        'leads': [{'id': lead.id, 'name': f'{lead.first_name} {lead.last_name}'} for lead in leads],
        'clients': [{'id': client.id, 'name': f'{client.first_name} {client.last_name}'} for client in clients],
        'users': [{'id': user.id, 'username': user.username} for user in users],
    }

    return JsonResponse(result_data)
