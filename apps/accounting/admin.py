from django.contrib import admin
from .models import Account, FiscalYear, FiscalPeriod, JournalEntry, JournalLine, ARInvoice, BankAccount, TaxRate


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 0
    readonly_fields = ['journal_entry']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'normal_balance', 'is_system', 'is_active']
    list_filter = ['account_type', 'is_system', 'is_active']
    search_fields = ['code', 'name']


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_closed']


@admin.register(FiscalPeriod)
class FiscalPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'fiscal_year', 'start_date', 'end_date', 'is_closed']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'entry_type', 'entry_date', 'total_debit', 'is_posted']
    list_filter = ['entry_type', 'is_posted']
    readonly_fields = ['entry_number', 'created_at', 'total_debit', 'total_credit']
    inlines = [JournalLineInline]


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'tax_type', 'is_default']
