from django.db import models
from apps.core.models import SoftDeleteModel


class Supplier(SoftDeleteModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    payment_terms = models.IntegerField(default=30, help_text='Days')
    currency = models.CharField(max_length=3, default='PGK')
    tax_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        ordering = ['name']
