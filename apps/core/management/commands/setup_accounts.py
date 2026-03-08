from django.core.management.base import BaseCommand


CHART_OF_ACCOUNTS = [
    # Assets
    ('1000', 'Cash in Hand', 'asset', 'debit'),
    ('1010', 'EFTPOS Clearing', 'asset', 'debit'),
    ('1100', 'Accounts Receivable', 'asset', 'debit'),
    ('1200', 'Inventory — Goods', 'asset', 'debit'),
    ('1210', 'Inventory — Fabric', 'asset', 'debit'),
    ('1500', 'Fixed Assets', 'asset', 'debit'),
    # Liabilities
    ('2000', 'Accounts Payable', 'liability', 'credit'),
    ('2100', 'GST Output Tax Payable', 'liability', 'credit'),
    ('2110', 'GST Input Tax Receivable', 'asset', 'debit'),
    ('2120', 'GST Clearing', 'liability', 'credit'),
    ('2200', 'SWT Payable', 'liability', 'credit'),
    ('2210', 'Provisional Tax Payable', 'liability', 'credit'),
    ('2220', 'CIT Payable', 'liability', 'credit'),
    ('2230', 'Withholding Tax Payable', 'liability', 'credit'),
    ('2300', 'Customer Deposits', 'liability', 'credit'),
    # Equity
    ('3000', "Owner's Equity", 'equity', 'credit'),
    ('3100', 'Retained Earnings', 'equity', 'credit'),
    # Revenue
    ('4000', 'Café Revenue', 'revenue', 'credit'),
    ('4100', 'Restaurant Revenue', 'revenue', 'credit'),
    ('4200', 'Tailoring Revenue', 'revenue', 'credit'),
    ('4300', 'Retail Sales Revenue', 'revenue', 'credit'),
    # COGS
    ('5000', 'Cost of Goods Sold — Food', 'cogs', 'debit'),
    ('5100', 'Cost of Goods Sold — Beverage', 'cogs', 'debit'),
    ('5200', 'Cost of Goods Sold — Fabric', 'cogs', 'debit'),
    ('5300', 'Cost of Goods Sold — Retail', 'cogs', 'debit'),
    # Expenses
    ('6000', 'Staff Wages', 'expense', 'debit'),
    ('6010', 'Wages — Café', 'expense', 'debit'),
    ('6020', 'Wages — Restaurant', 'expense', 'debit'),
    ('6030', 'Wages — Tailoring', 'expense', 'debit'),
    ('6040', 'Wages — Warehouse', 'expense', 'debit'),
    ('6050', 'Wages — Admin', 'expense', 'debit'),
    ('6060', 'Superannuation Expense', 'expense', 'debit'),
    ('6100', 'Rent', 'expense', 'debit'),
    ('6200', 'Utilities', 'expense', 'debit'),
    ('6300', 'Depreciation', 'expense', 'debit'),
    ('6400', 'Cash Variance', 'expense', 'debit'),
    ('6500', 'Stock Write-off', 'expense', 'debit'),
]


class Command(BaseCommand):
    help = 'Set up default Chart of Accounts for Harhurum POS'

    def handle(self, *args, **options):
        from apps.accounting.models import Account
        created_count = 0
        for code, name, account_type, normal_balance in CHART_OF_ACCOUNTS:
            _, created = Account.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'account_type': account_type,
                    'normal_balance': normal_balance,
                    'is_system': True,
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f'Chart of Accounts setup complete. {created_count} accounts created.'
        ))
