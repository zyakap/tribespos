from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, BusinessUnit
from apps.customers.models import Customer
from apps.products.models import Product, ProductVariant


class CashSession(TimeStampedModel):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed')]
    terminal_id = models.CharField(max_length=30)
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cash_sessions')
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.PROTECT)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_float = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    variance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.terminal_id} — {self.cashier} — {self.opened_at.date()}"

    class Meta:
        ordering = ['-opened_at']


class SaleOrder(TimeStampedModel):
    SALE_TYPES = [
        ('pos', 'POS Counter'),
        ('table', 'Table Service'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
        ('wholesale', 'Wholesale'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('held', 'Held'),
        ('completed', 'Completed'),
        ('void', 'Void'),
        ('refunded', 'Refunded'),
    ]
    order_number = models.CharField(max_length=30, unique=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.PROTECT, related_name='orders')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    sale_type = models.CharField(max_length=20, choices=SALE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    table_number = models.CharField(max_length=10, blank=True)
    covers = models.IntegerField(null=True, blank=True)
    cashier = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='cashier_orders')
    waiter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='waiter_orders')
    terminal_id = models.CharField(max_length=30, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    journal_entry_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.order_number

    def recalculate_totals(self):
        from decimal import Decimal
        lines = self.lines.all()
        subtotal = sum(l.line_total or Decimal('0') for l in lines)
        if lines and lines[0].tax_inclusive:
            tax = subtotal - (subtotal / Decimal('1.10'))
        else:
            tax = subtotal * Decimal('0.10')
        self.subtotal = subtotal
        self.tax_total = tax.quantize(Decimal('0.01'))
        self.total = subtotal
        self.save(update_fields=['subtotal', 'tax_total', 'total'])

    class Meta:
        ordering = ['-opened_at']


class SaleOrderLine(models.Model):
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=200)
    qty = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    tax_inclusive = models.BooleanField(default=True)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    course = models.CharField(max_length=20, blank=True)
    sent_to_kitchen = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        discount = self.discount_pct / Decimal('100')
        self.line_total = (self.qty * self.unit_price * (1 - discount)).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)


class OrderLineModifier(models.Model):
    line = models.ForeignKey(SaleOrderLine, on_delete=models.CASCADE, related_name='modifiers')
    modifier_name = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Payment(TimeStampedModel):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card_visa', 'Visa Card'),
        ('card_mastercard', 'Mastercard'),
        ('eftpos', 'EFTPOS'),
        ('mobile_money', 'Mobile Money'),
        ('account_credit', 'Account Credit'),
        ('voucher', 'Voucher'),
    ]
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    tendered = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    change_given = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    journal_entry_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.payment_method}: K{self.amount}"
