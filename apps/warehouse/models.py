from django.db import models
from django.contrib.auth.models import User
from apps.core.models import SoftDeleteModel, TimeStampedModel, BusinessUnit
from apps.products.models import Product, ProductVariant


class Warehouse(SoftDeleteModel):
    LOCATION_TYPES = [
        ('main', 'Main Warehouse'),
        ('cold_room', 'Cold Room'),
        ('bar', 'Bar'),
        ('kitchen', 'Kitchen'),
        ('fabric_store', 'Fabric Store'),
    ]
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='main')

    def __str__(self):
        return f"{self.business_unit.code} — {self.name}"

    class Meta:
        ordering = ['business_unit', 'name']


class StockLocation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_locations')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_locations')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_locations')
    qty_on_hand = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_reserved = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    @property
    def qty_available(self):
        return self.qty_on_hand - self.qty_reserved

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.qty_on_hand}"

    class Meta:
        unique_together = [('product', 'variant', 'warehouse')]
        ordering = ['product', 'warehouse']


class StockMovement(TimeStampedModel):
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase / GRN'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('production', 'Production'),
        ('waste', 'Waste / Write-off'),
        ('return', 'Return'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    qty = models.DecimalField(max_digits=12, decimal_places=3, help_text='Positive=in, Negative=out')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='stock_movements')

    def __str__(self):
        direction = '+' if self.qty >= 0 else ''
        return f"{self.movement_type}: {self.product.sku} {direction}{self.qty}"

    class Meta:
        ordering = ['-created_at']
