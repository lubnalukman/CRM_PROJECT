# forms.py
from django import forms
from .models import Lead
from .models import LeadSource
from django import forms
from .models import Lead
from django.contrib.auth import get_user_model

User = get_user_model()

class LeadForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),  # Populate with users
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'source', 'status', 'tags', 'notes', 'assigned_to']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically fetch LeadSource objects for dropdown
        self.fields['source'].queryset = LeadSource.objects.all()

class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ['source', 'description']
        widgets = {
            'source': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 rounded w-full', 'rows': 3}),
        }