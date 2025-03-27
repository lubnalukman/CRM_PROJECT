from django.urls import path
from . import views

urlpatterns = [

path('clientlist/',views.clients_list,name='clients_list'),
path('create_clients/',views.create_client,name='create_client'),
path('client_details/<int:client_id>/',views.client_details,name='client_details'),
path('edit_client/<int:client_id>/', views.edit_client, name='edit_client'),
path('delete_client/<int:client_id>/', views.delete_lead, name='delete_client'), 
]