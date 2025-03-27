#usersapp/urls.py
from django.urls import path,include
from  . import views
from .views import request_otp, verify_otp, reset_password


urlpatterns = [
    path('',views.index,name='index'),
    path('request_otp/', request_otp, name='request_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('reset_password/', reset_password, name='reset_password'),
    path('accounts/logout/',views.logout_user,name='logout'),
    path('signup/',views.signup_user, name='signup'), 
    path('login/', views.custom_login, name='custom_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manager/dashboard/',views.manager_dashboard, name='manager_dashboard'),
    path('salesrep/dashboard/',views.salesrep_dashboard, name='salesrep_dashboard'),
    path('viewer/dashboard/', views.viewer_dashboard, name='viewer_dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('profile/', views.user_profile, name='user_profile'),
    path('search/', views.search, name='search'),

]