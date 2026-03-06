from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Account, JournalEntry, JournalLine, FiscalPeriod
from apps.core.utils import generate_sequence_number


def get_account(code: str) -> Account:
    return Account.objects.get(code=code)


def get_or_create_fiscal_period(date) -> FiscalPeriod:
    try:
        return FiscalPeriod.objects.get(start_date__lte=date, end_date__gte=date)
    except FiscalPeriod.DoesNotExist:
        return None


@transaction.atomic
def create_journal_entry(entry_type: str, entry_date, description: str,
                          lines: list, reference_type='', reference_id=None, user=None) -> JournalEntry:
    """
    Create a double-entry journal entry.
    lines: list of {'account_code': str, 'debit': Decimal, 'credit': Decimal, 'description': str}
    """
    fiscal_period = get_or_create_fiscal_period(entry_date)

    je = JournalEntry.objects.create(
        entry_number=generate_sequence_number(JournalEntry, 'JE', 'entry_number'),
        entry_type=entry_type,
        reference_type=reference_type,
        reference_id=reference_id,
        fiscal_period=fiscal_period,
        entry_date=entry_date,
        description=description,
        is_posted=True,
        created_by=user,
    )

    total_debit = Decimal('0')
    total_credit = Decimal('0')

    for i, line_data in enumerate(lines):
        account = get_account(line_data['account_code'])
        debit = Decimal(str(line_data.get('debit', 0)))
        credit = Decimal(str(line_data.get('credit', 0)))
        JournalLine.objects.create(
            journal_entry=je,
            account=account,
            description=line_data.get('description', ''),
            debit=debit,
            credit=credit,
            sort_order=i,
        )
        total_debit += debit
        total_credit += credit

    je.total_debit = total_debit
    je.total_credit = total_credit
    je.save(update_fields=['total_debit', 'total_credit'])
    return je


def _get_revenue_account(business_unit):
    from .journal_rules import REVENUE_ACCOUNTS
    return REVENUE_ACCOUNTS.get(business_unit.unit_type, '4300')


def post_sale_journal(order, payments):
    """Post journal entry for a completed sale."""
    from apps.pos.models import Payment
    date = timezone.now().date()
    lines = []

    # DR Cash/EFTPOS/AR based on payment method
    for pdata in payments:
        method = pdata.get('payment_method', 'cash')
        amount = Decimal(str(pdata['amount']))
        if method == 'cash':
            dr_account = '1000'
        elif method in ('card_visa', 'card_mastercard', 'eftpos'):
            dr_account = '1010'
        else:
            dr_account = '1100'
        lines.append({'account_code': dr_account, 'debit': amount, 'description': f'Payment: {method}'})

    revenue_code = _get_revenue_account(order.business_unit)
    subtotal = order.subtotal
    tax = order.tax_total

    lines.append({'account_code': revenue_code, 'credit': subtotal, 'description': 'Sales revenue'})
    if tax > 0:
        lines.append({'account_code': '2100', 'credit': tax, 'description': 'GST Payable'})

    create_journal_entry(
        'sale', date, f'Sale {order.order_number}',
        lines, 'SaleOrder', order.id
    )


def post_tailoring_deposit(order, deposit_amount, user=None):
    lines = [
        {'account_code': '1000', 'debit': deposit_amount, 'description': 'Deposit received'},
        {'account_code': '2200', 'credit': deposit_amount, 'description': 'Customer deposit liability'},
    ]
    create_journal_entry('receipt', timezone.now().date(),
        f'Tailoring deposit {order.order_number}', lines,
        'TailoringOrder', order.id, user)


def post_tailoring_collection(order, balance_payment, user=None):
    from .journal_rules import REVENUE_ACCOUNTS
    deposit = order.deposit_paid - balance_payment
    subtotal = order.total / Decimal('1.10')
    tax = order.total - subtotal
    fabric_cost = (order.fabric_product.cost_price * order.fabric_qty) if order.fabric_product and order.fabric_qty else Decimal('0')

    lines = [
        {'account_code': '2200', 'debit': deposit, 'description': 'Reverse deposit'},
        {'account_code': '1000', 'debit': balance_payment, 'description': 'Balance collected'},
        {'account_code': '4200', 'credit': subtotal, 'description': 'Tailoring revenue'},
        {'account_code': '2100', 'credit': tax, 'description': 'GST Payable'},
    ]
    if fabric_cost > 0:
        lines += [
            {'account_code': '5200', 'debit': fabric_cost, 'description': 'Fabric COGS'},
            {'account_code': '1210', 'credit': fabric_cost, 'description': 'Inventory Fabric'},
        ]
    create_journal_entry('sale', timezone.now().date(),
        f'Tailoring collection {order.order_number}', lines,
        'TailoringOrder', order.id, user)
