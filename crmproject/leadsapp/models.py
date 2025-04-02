
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

    def __str__(self):
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
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_leads',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Communication(models.Model):
    INTERACTION_TYPES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('chat', 'Chat'),
        ('meeting', 'Meeting'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='communications')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES, default='email')
    subject = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,related_name='updated_communications', blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['lead']),
        ]

    def __str__(self):
        return f"{self.interaction_type} with {self.lead} on {self.timestamp.strftime('%Y-%m-%d')}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)