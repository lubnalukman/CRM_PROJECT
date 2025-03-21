# forms.py
from django import forms
from .models import Lead
from .models import LeadSource
from .models import Communication
from django.contrib.auth import get_user_model

User = get_user_model()

class LeadForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,  # Allows multiple selection
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
        self.fields['assigned_to'].queryset = User.objects.filter(user_type__in=["sales_manager", "sales_rep"])
        self.fields['source'].queryset = LeadSource.objects.all()

class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ['source', 'description']
        widgets = {
            'source': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 rounded w-full', 'rows': 3}),
        }

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['interaction_type', 'subject', 'notes', 'attachment']
        widgets = {
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter notes'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

        def save(self, commit=True):
            instance = super().save(commit=False)
        
        # If this is an update, set `updated_by` to the logged-in user
            if instance.pk:
                instance.updated_by = instance.created_by  # or request.user if modifying communication
        
            if commit:
                instance.save()
            return instance