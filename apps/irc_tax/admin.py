from django.contrib import admin
from .models import GSTReturn, GSTReturnLine, Employee, PayrollRun, PayrollLine, SWTRemittance, CITReturn, ProvisionalTaxInstalment, WithholdingTaxTransaction


class GSTReturnLineInline(admin.TabularInline):
    model = GSTReturnLine
    extra = 0


@admin.register(GSTReturn)
class GSTReturnAdmin(admin.ModelAdmin):
    list_display = ['return_period', 'status', 'output_tax_collected', 'input_tax_credits', 'net_gst_payable', 'due_date']
    list_filter = ['status']
    inlines = [GSTReturnLineInline]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'tax_status', 'pay_frequency', 'base_salary', 'is_active']


class PayrollLineInline(admin.TabularInline):
    model = PayrollLine
    extra = 0


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ['pay_period_start', 'pay_period_end', 'status', 'total_gross', 'total_swt', 'total_net']
    inlines = [PayrollLineInline]


@admin.register(SWTRemittance)
class SWTRemittanceAdmin(admin.ModelAdmin):
    list_display = ['remittance_month', 'status', 'total_gross_wages', 'total_swt_withheld', 'due_date']


@admin.register(CITReturn)
class CITReturnAdmin(admin.ModelAdmin):
    list_display = ['tax_year', 'status', 'taxable_income', 'gross_cit', 'net_cit_payable', 'due_date']


@admin.register(WithholdingTaxTransaction)
class WHTAdmin(admin.ModelAdmin):
    list_display = ['payment_date', 'wht_type', 'payee_name', 'gross_amount', 'wht_amount', 'remitted_to_irc']
