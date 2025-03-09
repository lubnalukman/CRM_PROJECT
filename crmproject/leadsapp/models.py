
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class LeadSource(models.Model):
    SOURCE_CHOICES = (
        ('web_form', 'Web Form'),  # Default source for customer signups
        ('email', 'Email'),
        ('manual_entry', 'Manual Entry'),
        ('api', 'API Integration'),
    )
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='web_form')  # Default source
    description = models.TextField(blank=True, null=True)

    def _str_(self):
        return self.source

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    source = models.ForeignKey(LeadSource,on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    tags = models.CharField(max_length=100, blank=True, null=True)  # For categorization
    notes = models.TextField(blank=True, null=True)  # No default notes
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.first_name} {self.last_name}"