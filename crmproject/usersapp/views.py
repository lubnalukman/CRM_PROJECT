from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail

def index(request):
    return render(request,"index.html")

def login_user(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        
        user = authenticate(request, username=uname, password=pwd)
        
        if user is not None:
            login(request, user)
            if user.user_type == 'admin':
                return redirect('admin_home')  
            elif user.user_type == 'sales_manager':
                return redirect('sales_manager_home')  
            elif user.user_type == 'sales_rep':
                return redirect('sales_rep_home')  
            elif user.user_type == 'viewer':
                return redirect('viewer_home') 
            else:
                return redirect('home')  
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login') 
    else:
        return render(request, 'registration/login.html')


def logout_user(request):
    logout(request)
    messages.success(request,"You have been logged out")

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
            return redirect('login')
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

