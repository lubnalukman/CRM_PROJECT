
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('sales_manager', 'Sales Manager'),
        ('sales_rep', 'Sales Representative'),
        ('viewer', 'Viewer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='viewer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  