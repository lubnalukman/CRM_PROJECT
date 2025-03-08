from django.contrib import admin
from .models import Lead
from .forms import LeadForm

class LeadAdmin(admin.ModelAdmin):
    form=LeadForm
    list_display = ('first_name', 'last_name', 'email', 'status', 'source','notes','tags', 'assigned_to','created_at','updated_at')
    list_filter = ('status', 'source', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email')

admin.site.register(Lead, LeadAdmin)