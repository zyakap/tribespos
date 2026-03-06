"""
Automated journal posting rules for Harhurum POS.
"""

POSTING_RULES = {
    'cash_sale': [
        ('DR', '1000', 'total_including_tax'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'eftpos_sale': [
        ('DR', '1010', 'total_including_tax'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'account_sale': [
        ('DR', '1100', 'total_including_tax'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'cogs_deduction': [
        ('DR', 'cogs_account', 'cost_of_goods'),
        ('CR', 'inventory_account', 'cost_of_goods'),
    ],
    'purchase_invoice': [
        ('DR', 'inventory_account', 'subtotal'),
        ('DR', '2110', 'tax_amount'),
        ('CR', '2000', 'total'),
    ],
    'ap_payment': [
        ('DR', '2000', 'amount'),
        ('CR', '1000', 'amount'),
    ],
    'tailoring_deposit': [
        ('DR', '1000', 'deposit_amount'),
        ('CR', '2200', 'deposit_amount'),
    ],
    'tailoring_collection': [
        ('DR', '2200', 'deposit_amount'),
        ('DR', '1000', 'balance_paid'),
        ('CR', '4200', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
        ('DR', '5200', 'fabric_cost'),
        ('CR', '1210', 'fabric_cost'),
    ],
    'swt_payroll': [
        ('DR', '6000', 'gross_wages'),
        ('CR', '2200', 'swt_amount'),
        ('CR', '1000', 'net_pay'),
    ],
}

# Revenue account mapping by business unit type
REVENUE_ACCOUNTS = {
    'cafe': '4000',
    'restaurant': '4100',
    'tailoring': '4200',
    'warehouse': '4300',
}

COGS_ACCOUNTS = {
    'cafe_food': '5000',
    'cafe_beverage': '5100',
    'fabric': '5200',
    'retail': '5300',
}

INVENTORY_ACCOUNTS = {
    'goods': '1200',
    'fabric': '1210',
}
