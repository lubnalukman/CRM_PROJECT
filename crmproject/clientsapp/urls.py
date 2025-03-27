from django.urls import path
from . import views

urlpatterns = [

path('clientlist/',views.clients_list,name='clients_list'),
path('create_clients/',views.create_client,name='create_client'),
]