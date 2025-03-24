from django.db import models

# Create your models here.
from django.db import models
from leadsapp.models import Lead

class SalesStage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # Optional description
    order = models.IntegerField(unique=True)  # For ordering stages
    is_active = models.BooleanField(default=True)  # Enable/disable stages

    class Meta:
        ordering = ['order']  # Ensure proper ordering

    def __str__(self):
        return self.name

class SalesPipeline(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='pipeline')
    stage = models.ForeignKey(SalesStage, on_delete=models.SET_NULL, null=True, blank=True)
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Probability of closing
    expected_close_date = models.DateField(blank=True, null=True)  # Expected closing date
    notes = models.TextField(blank=True, null=True)  # Internal notes
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation
    updated_at = models.DateTimeField(auto_now=True)  # Track last update

    def __str__(self):
        return f"{self.lead} - {self.stage}"

    class Meta:
        ordering = ['-updated_at']  # Show most recent updates first
