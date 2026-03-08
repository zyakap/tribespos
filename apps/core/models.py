from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_active = False
        self.save()


class BusinessUnit(SoftDeleteModel):
    UNIT_TYPES = [
        ('cafe', 'Café'),
        ('restaurant', 'Restaurant'),
        ('tailoring', 'Tailoring'),
        ('warehouse', 'Warehouse / Retail'),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        ordering = ['code']
