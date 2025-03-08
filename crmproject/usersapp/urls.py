from django.urls import path,include
from . import views
from .views import request_otp, verify_otp, reset_password


urlpatterns = [
    path('',views.index,name='index'),
    path('accounts/login/',views.login_user,name='login'),
    path('request_otp/', views.request_otp, name='request_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('accounts/logout/',views.logout_user,name='logout'),
    path('signup/', views.signup_admin, name='signup'), 
    
]