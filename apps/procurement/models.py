from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.suppliers.models import Supplier
from apps.products.models import Product, ProductVariant
from apps.warehouse.models import Warehouse


class PurchaseOrder(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partial', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    po_number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='purchase_orders')

    def __str__(self):
        return self.po_number

    def recalculate_totals(self):
        from decimal import Decimal
        subtotal = sum(line.line_total or 0 for line in self.lines.all())
        tax = subtotal * Decimal('0.10')
        self.subtotal = subtotal
        self.tax_total = tax
        self.total = subtotal + tax
        self.save(update_fields=['subtotal', 'tax_total', 'total'])

    class Meta:
        ordering = ['-order_date', '-created_at']


class PurchaseOrderLine(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    qty_ordered = models.DecimalField(max_digits=12, decimal_places=3)
    qty_received = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, null=True)

    def save(self, *args, **kwargs):
        self.line_total = self.qty_ordered * self.unit_cost
        super().save(*args, **kwargs)


class GoodsReceivedNote(TimeStampedModel):
    grn_number = models.CharField(max_length=30, unique=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    received_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_posted = models.BooleanField(default=False)

    def __str__(self):
        return self.grn_number


class GRNLine(models.Model):
    grn = models.ForeignKey(GoodsReceivedNote, on_delete=models.CASCADE, related_name='lines')
    po_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    qty_received = models.DecimalField(max_digits=12, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4)


class SupplierInvoice(TimeStampedModel):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    invoice_number = models.CharField(max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='invoices')
    po = models.ForeignKey(PurchaseOrder, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    journal_entry_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.invoice_number} — {self.supplier.name}"
