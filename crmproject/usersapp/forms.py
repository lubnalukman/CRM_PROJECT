from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError   # Import the field

class PhoneNumberMixin:
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number',None)
        if not phone_number:  # If the field is empty, return None
            return None
        return phone_number
        '''if phone_number:
            if not phone_number.is_valid():
                raise ValidationError("Enter a valid phone number.")
        return phone_number'''


class SignupForm(UserCreationForm, PhoneNumberMixin):
    phone_number = PhoneNumberField(
        required=False,  
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'}),
        help_text="Format: +1234567890"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }

class UserForm(forms.ModelForm,PhoneNumberMixin): 
    phone_number = PhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'is_verified', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    

class UserProfileForm(forms.ModelForm, PhoneNumberMixin):
    phone_number = PhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class UserEditForm(forms.ModelForm, PhoneNumberMixin):
    phone_number = PhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'is_verified']
        widgets = {
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    