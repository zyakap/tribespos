from django.db import models
from apps.core.models import TimeStampedModel, BusinessUnit
from apps.pos.models import SaleOrder


class RestaurantTable(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning'),
    ]
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    section = models.CharField(max_length=50, blank=True)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_order = models.ForeignKey(SaleOrder, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Table {self.table_number} ({self.business_unit.code})"

    class Meta:
        ordering = ['table_number']
        unique_together = [('business_unit', 'table_number')]


class KitchenTicket(TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
    ]
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='kitchen_tickets')
    ticket_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.ticket_number} for {self.order.order_number}"

    class Meta:
        ordering = ['-created_at']


class KitchenTicketLine(models.Model):
    ticket = models.ForeignKey(KitchenTicket, on_delete=models.CASCADE, related_name='lines')
    order_line = models.ForeignKey('pos.SaleOrderLine', on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.TextField(blank=True)
