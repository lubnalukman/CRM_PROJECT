from django.contrib import admin

# Register your models here.

from .models import SalesPipeline,SalesStage

# Register your models here.
admin.site.register(SalesStage)
admin.site.register(SalesPipeline)