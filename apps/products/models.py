from django.db import models
from apps.core.models import SoftDeleteModel, TimeStampedModel, BusinessUnit
import uuid


class Category(TimeStampedModel):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    name = models.CharField(max_length=100)
    business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.SET_NULL, related_name='categories')
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=30)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

    class Meta:
        ordering = ['name']
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'


class Product(SoftDeleteModel):
    PRODUCT_TYPES = [
        ('goods', 'Goods'),
        ('service', 'Service'),
        ('composite', 'Composite / Menu Item'),
        ('fabric', 'Fabric'),
    ]
    GST_SUPPLY_TYPES = [
        ('T', 'Taxable (10%)'),
        ('Z', 'Zero-Rated'),
        ('E', 'Exempt'),
        ('OS', 'Out of Scope'),
    ]
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    uom = models.ForeignKey(UnitOfMeasure, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='goods')
    cost_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell_price_wholesale = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    tax_inclusive = models.BooleanField(default=True)
    gst_supply_type = models.CharField(max_length=2, choices=GST_SUPPLY_TYPES, default='T')
    track_inventory = models.BooleanField(default=True)
    min_stock_level = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reorder_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.sku} — {self.name}"

    class Meta:
        ordering = ['name']


class ProductVariant(SoftDeleteModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku_suffix = models.CharField(max_length=20, blank=True)
    attribute_json = models.JSONField(default=dict)
    barcode = models.CharField(max_length=50, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.sku}{self.sku_suffix}"


class BOMItem(models.Model):
    parent_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_items')
    component_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_in_bom')
    quantity = models.DecimalField(max_digits=12, decimal_places=4)

    def __str__(self):
        return f"{self.parent_product} → {self.component_product} × {self.quantity}"

    class Meta:
        verbose_name = 'Bill of Materials Item'
