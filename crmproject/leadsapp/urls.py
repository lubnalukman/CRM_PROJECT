
# leadsapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Lead Management
    path('leads/', views.all_leads, name='all_leads'),
    path('leads/create/', views.create_lead, name='create_lead'),
    path('leads/edit/<int:lead_id>/', views.edit_lead, name='edit_lead'),
    path('leads/delete/<int:lead_id>/', views.delete_lead, name='delete_lead'), 
    path('lead/<int:lead_id>/', views.lead_detail, name='lead_detail'),
   

    # User Management
    
]
