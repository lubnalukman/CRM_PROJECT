from django.urls import path,include
from .views import *
from .views import request_otp, verify_otp, reset_password


urlpatterns = [
    path('',index,name='index'),
    path('accounts/login/',login_user,name='login'),
    path('request_otp/', request_otp, name='request_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('reset_password/', reset_password, name='reset_password'),
    path('accounts/logout/',logout_user,name='logout'),
    path('signup/',signup_user, name='signup'), 
    
]