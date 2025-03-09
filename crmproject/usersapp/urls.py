#usersapp/urls.py
from django.urls import path,include
from .views import *
from .views import request_otp, verify_otp, reset_password


urlpatterns = [
    path('',index,name='index'),
    path('request_otp/', request_otp, name='request_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('reset_password/', reset_password, name='reset_password'),
    path('accounts/logout/',logout_user,name='logout'),
    path('signup/',signup_user, name='signup'), 
    path('login/', custom_login, name='custom_login'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('manager/dashboard/',manager_dashboard, name='manager_dashboard'),
    path('salesrep/dashboard/',salesrep_dashboard, name='salesrep_dashboard'),
    path('viewer/dashboard/', viewer_dashboard, name='viewer_dashboard'),
]