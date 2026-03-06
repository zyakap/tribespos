from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel, BusinessUnit


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('cogs', 'Cost of Goods Sold'),
    ]
    NORMAL_BALANCE = [('debit', 'Debit'), ('credit', 'Credit')]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_subtype = models.CharField(max_length=50, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    is_system = models.BooleanField(default=False)
    normal_balance = models.CharField(max_length=10, choices=NORMAL_BALANCE)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        ordering = ['code']


class FiscalYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class FiscalPeriod(models.Model):
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fiscal_year.name} / {self.name}"

    class Meta:
        ordering = ['start_date']


class JournalEntry(TimeStampedModel):
    ENTRY_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('adjustment', 'Adjustment'),
        ('payroll', 'Payroll'),
        ('depreciation', 'Depreciation'),
        ('manual', 'Manual'),
    ]
    entry_number = models.CharField(max_length=30, unique=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    fiscal_period = models.ForeignKey(FiscalPeriod, null=True, blank=True, on_delete=models.SET_NULL)
    entry_date = models.DateField()
    description = models.TextField(blank=True)
    total_debit = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    total_credit = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    is_posted = models.BooleanField(default=False)
    is_reconciled = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.entry_number} ({self.entry_type})"

    class Meta:
        ordering = ['-entry_date', '-created_at']


class JournalLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.SET_NULL)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']


class ARInvoice(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('partial', 'Partial'),
        ('paid', 'Paid'), ('overdue', 'Overdue'), ('void', 'Void'),
    ]
    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='ar_invoices')
    sale_order = models.ForeignKey('pos.SaleOrder', null=True, blank=True, on_delete=models.SET_NULL)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    outstanding = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    journal_entry = models.ForeignKey(JournalEntry, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.invoice_number


class BankAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bsb_or_branch = models.CharField(max_length=30, blank=True)
    currency = models.CharField(max_length=3, default='PGK')
    current_balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bank_name} — {self.account_number}"


class TaxRate(models.Model):
    TAX_TYPES = [('gst', 'GST'), ('import', 'Import'), ('exempt', 'Exempt'), ('zero', 'Zero-rated')]
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_type = models.CharField(max_length=10, choices=TAX_TYPES, default='gst')
    sales_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales_tax_rates')
    purchase_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchase_tax_rates')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
