from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.customers.models import Customer
from apps.products.models import Product


class TailoringOrder(TimeStampedModel):
    STATUS_CHOICES = [
        ('quote', 'Quote'),
        ('confirmed', 'Confirmed'),
        ('cutting', 'Cutting'),
        ('sewing', 'Sewing'),
        ('finishing', 'Finishing'),
        ('ready', 'Ready for Collection'),
        ('collected', 'Collected'),
        ('cancelled', 'Cancelled'),
    ]
    order_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='tailoring_orders')
    tailor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='tailoring_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quote')
    garment_type = models.CharField(max_length=100)
    style_notes = models.TextField(blank=True)
    measurements_json = models.JSONField(default=dict, blank=True)
    fabric_product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL, related_name='tailoring_orders'
    )
    fabric_qty = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    labour_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fabric_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    additional_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    promised_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    collected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_tailoring_orders')

    def __str__(self):
        return f"{self.order_number} — {self.customer.name}"

    def recalculate_total(self):
        self.total = (
            self.labour_charge + self.fabric_charge + self.additional_charge - self.discount_amount
        )
        self.balance_due = self.total - self.deposit_paid
        self.save(update_fields=['total', 'balance_due'])

    class Meta:
        ordering = ['-created_at']


class TailoringStageLog(TimeStampedModel):
    tailoring_order = models.ForeignKey(TailoringOrder, on_delete=models.CASCADE, related_name='stage_logs')
    stage = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.tailoring_order.order_number} → {self.stage}"

    class Meta:
        ordering = ['created_at']
