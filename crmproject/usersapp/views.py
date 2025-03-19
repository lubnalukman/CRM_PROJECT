from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import User
#from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail
from .forms import SignupForm
from leadsapp.models import Lead, LeadSource
from django.contrib.auth.decorators import login_required
from usersapp.forms import UserForm,UserProfileForm, UserEditForm
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model 
from django.contrib.auth.forms import AuthenticationForm
import logging


def index(request):
    return render(request,"index.html")

User = get_user_model()

logger = logging.getLogger(__name__)

def signup_user(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create and save the user
            user = form.save(commit=False)
            user.user_type = 'viewer'  # Assign default user type
            user.save()

            try:
                # Fetch an existing LeadSource with 'web_form', or create if none exists
                lead_source = LeadSource.objects.filter(source='web_form').first()
                
                if not lead_source:
                    lead_source = LeadSource.objects.create(
                        source='web_form',
                        description='Leads from web form signups'
                    )
                
                # Create the lead with user details
                lead = Lead.objects.create(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone_number = form.cleaned_data.get('phone_number', ''),
                    source=lead_source,  # Assign the LeadSource instance
                    status='new',  # Default status
                    assigned_to=None,  # No assigned user by default
                    notes='',  # Empty string instead of None
                    tags=''  # Empty string instead of None
                )

                # Redirect after successful signup
                messages.success(request, "Signup successful! Please log in.")
                return redirect('custom_login')  # Change to your actual dashboard URL

            except Exception as e:
                logger.error(f"Error creating lead: {e}") # Log the error
                user.delete()  # Rollback user creation if lead creation fails
                form.add_error(None, "An error occurred while creating the lead. Please try again.")

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
    
@login_required
def user_profile(request):
    user = request.user  # Get the logged-in user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
        else:
            messages.error(request, "Error updating profile. Please check the form.")
    else:
        form = UserProfileForm(instance=user)  # Prefill form with user data

    return render(request, 'user_profile.html', {'form': form})

def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    if request.user.user_type != 'admin':
        return redirect('custom_login')  # Or some unauthorized page
    return render(request, 'admin_dashboard.html')

def manager_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    if request.user.user_type != 'sales_manager':
        return redirect('custom_login')
    return render(request, 'salesmanager_dashboard.html')

def salesrep_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    if request.user.user_type != 'sales_rep':
        return redirect('custom_login')
    return render(request, 'salesrep_dashboard.html')

def viewer_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    if request.user.user_type != 'viewer':
        return redirect('custom_login')
    return render(request, 'viewer_dashboard.html')


@login_required
def all_users(request):
    # Fetch all users
    users = User.objects.all()
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the template with the paginated users
    return render(request, 'all_users.html', {'page_obj': page_obj})

@login_required
def create_user(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    
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
            return redirect('all_users')
    else:
        form = UserForm()
    
    return render(request, 'create_user.html', {'form': form})


@login_required
def edit_user(request, user_id):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('all_users')
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})


@login_required
def delete_user(request, user_id):
    if not request.user.is_authenticated:
        return redirect('custom_login')
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('all_users')

@login_required
def user_detail(request, user_id):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('custom_login')
    
    # Fetch the user or return a 404 error
    user = get_object_or_404(User, id=user_id)
    
    # Render the user detail template
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

