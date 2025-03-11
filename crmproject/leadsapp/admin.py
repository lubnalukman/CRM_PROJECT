from django.contrib import admin
from .models import Lead, LeadSource

# Register your models here.
admin.site.register(Lead)
admin.site.register(LeadSource)