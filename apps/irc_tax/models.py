from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel


class GSTReturn(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('finalised', 'Finalised'), ('filed', 'Filed'), ('amended', 'Amended')]
    return_period = models.CharField(max_length=7, unique=True)
    period_start = models.DateField()
    period_end = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    total_taxable_sales = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    output_tax_collected = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_zero_rated_sales = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_exempt_sales = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_gross_sales = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_taxable_purchases = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    input_tax_credits = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_gst_payable = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_gst_refundable = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    adjustments_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    adjustment_notes = models.TextField(blank=True)
    filed_date = models.DateField(null=True, blank=True)
    filed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    irc_reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"GST Return {self.return_period} ({self.status})"

    class Meta:
        ordering = ['-return_period']


class GSTReturnLine(models.Model):
    LINE_TYPES = [('output', 'Output Tax'), ('input', 'Input Tax Credit'), ('adjustment', 'Adjustment')]
    gst_return = models.ForeignKey(GSTReturn, on_delete=models.CASCADE, related_name='lines')
    line_type = models.CharField(max_length=20, choices=LINE_TYPES)
    transaction_type = models.CharField(max_length=50, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    transaction_date = models.DateField()
    supplier_customer = models.CharField(max_length=150, blank=True)
    description = models.CharField(max_length=255, blank=True)
    gst_exclusive_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    gst_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    supply_type = models.CharField(max_length=10, blank=True)


class Employee(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    irc_tin = models.CharField(max_length=20, blank=True)
    tax_status = models.CharField(max_length=20, choices=[('resident', 'Resident'), ('non_resident', 'Non-Resident')], default='resident')
    pay_frequency = models.CharField(max_length=20, choices=[('fortnightly', 'Fortnightly'), ('monthly', 'Monthly')], default='fortnightly')
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bsp_branch = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.get_full_name() or self.user.username)


class PayrollRun(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('approved', 'Approved'), ('paid', 'Paid')]
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    pay_date = models.DateField()
    period_number = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_swt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='payroll_runs')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_payroll_runs')

    def __str__(self):
        return f"Payroll {self.pay_period_start} — {self.pay_period_end}"


class PayrollLine(models.Model):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='lines')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    gross_wages = models.DecimalField(max_digits=12, decimal_places=2)
    housing_benefit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vehicle_benefit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_benefits = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_taxable = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    swt_deducted = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    is_resident = models.BooleanField(default=True)
    notes = models.TextField(blank=True)


class SWTRemittance(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('filed', 'Filed'), ('paid', 'Paid')]
    remittance_month = models.CharField(max_length=7, unique=True)
    due_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()
    total_gross_wages = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_swt_withheld = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    employee_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    filed_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    irc_reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"SWT Remittance {self.remittance_month}"


class CITReturn(TimeStampedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('finalised', 'Finalised'), ('filed', 'Filed')]
    tax_year = models.IntegerField(unique=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    exempt_income = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    assessable_income = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cogs = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    operating_expenses = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    depreciation = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    interest_expense = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    taxable_income = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    gross_cit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    provisional_tax_paid = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    swt_credits = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_cit_payable = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    filed_date = models.DateField(null=True, blank=True)
    irc_reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"CIT Return FY{self.tax_year}"


class ProvisionalTaxInstalment(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')]
    tax_year = models.IntegerField()
    quarter = models.IntegerField()
    due_date = models.DateField()
    estimated_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = [('tax_year', 'quarter')]


class WithholdingTaxTransaction(TimeStampedModel):
    WHT_TYPES = [('dividend', 'Dividend'), ('interest', 'Interest'), ('royalty', 'Royalty'), ('management_fee', 'Management Fee')]
    wht_type = models.CharField(max_length=20, choices=WHT_TYPES)
    payment_date = models.DateField()
    payee_name = models.CharField(max_length=150)
    payee_tin = models.CharField(max_length=20, blank=True)
    payee_residence = models.CharField(max_length=20, choices=[('resident', 'Resident'), ('non_resident', 'Non-Resident')], default='resident')
    gross_amount = models.DecimalField(max_digits=14, decimal_places=2)
    wht_rate = models.DecimalField(max_digits=5, decimal_places=2)
    wht_amount = models.DecimalField(max_digits=14, decimal_places=2)
    net_paid = models.DecimalField(max_digits=14, decimal_places=2)
    remitted_to_irc = models.BooleanField(default=False)
    remittance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"WHT {self.wht_type}: {self.payee_name}"
