
# leadsapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Lead Management
    path('leads-list/', views.leads_list, name='leads_list'),
    path('create_lead/', views.create_lead, name='create_lead'),
    path('edit_lead/<int:lead_id>/', views.edit_lead, name='edit_lead'),
    path('delete_lead/<int:lead_id>/', views.delete_lead, name='delete_lead'), 
    path('lead_details/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('lead_source_list',views.lead_source_list,name='lead_source'),
    path('create_lead_source/', views.create_lead_source, name='create_lead_source'),
    path('lead-source/edit/<int:source_id>/', views.edit_lead_source, name='edit_lead_source'),
    path('lead-source/delete/<int:source_id>/', views.delete_lead_source, name='delete_lead_source'),
    path('leads/<int:lead_id>/communication/<int:communication_id>/edit/', views.edit_communication, name='edit_communication'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read')

   
]
