from django.db import models
from apps.core.models import SoftDeleteModel


class Customer(SoftDeleteModel):
    CUSTOMER_TYPES = [
        ('walk_in', 'Walk-in'),
        ('account', 'Account Customer'),
        ('wholesale', 'Wholesale'),
    ]
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.IntegerField(default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='walk_in')

    def __str__(self):
        return f"{self.code} — {self.name}" if self.code else self.name

    def save(self, *args, **kwargs):
        if not self.code:
            last = Customer.objects.order_by('id').last()
            self.code = f"CUST-{(last.id + 1 if last else 1):05d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
