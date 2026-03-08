from decimal import Decimal
from django.db.models import Sum
from .models import Account, JournalLine


def _account_balance(code_prefix: str, date_range=None) -> Decimal:
    qs = JournalLine.objects.filter(
        account__code__startswith=code_prefix,
        journal_entry__is_posted=True,
    )
    if date_range:
        qs = qs.filter(journal_entry__entry_date__range=date_range)
    result = qs.aggregate(dr=Sum('debit'), cr=Sum('credit'))
    return (result['dr'] or Decimal('0')) - (result['cr'] or Decimal('0'))


def generate_pl(start, end):
    date_range = (start, end)

    def revenue(prefix):
        qs = JournalLine.objects.filter(
            account__code__startswith=prefix,
            account__account_type='revenue',
            journal_entry__is_posted=True,
            journal_entry__entry_date__range=date_range,
        )
        r = qs.aggregate(dr=Sum('debit'), cr=Sum('credit'))
        return (r['cr'] or Decimal('0')) - (r['dr'] or Decimal('0'))

    def expense(prefix):
        qs = JournalLine.objects.filter(
            account__code__startswith=prefix,
            account__account_type__in=['expense', 'cogs'],
            journal_entry__is_posted=True,
            journal_entry__entry_date__range=date_range,
        )
        r = qs.aggregate(dr=Sum('debit'), cr=Sum('credit'))
        return (r['dr'] or Decimal('0')) - (r['cr'] or Decimal('0'))

    total_revenue = revenue('4')
    total_cogs = expense('5')
    total_expenses = expense('6')
    gross_profit = total_revenue - total_cogs
    net_profit = gross_profit - total_expenses

    return {
        'total_revenue': total_revenue,
        'total_cogs': total_cogs,
        'gross_profit': gross_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'depreciation': expense('63'),
    }


def generate_trial_balance(date=None):
    from django.utils import timezone
    if date is None:
        date = timezone.now().date()
    accounts = Account.objects.filter(is_active=True).order_by('code')
    rows = []
    for acc in accounts:
        qs = JournalLine.objects.filter(
            account=acc, journal_entry__is_posted=True,
            journal_entry__entry_date__lte=date,
        ).aggregate(dr=Sum('debit'), cr=Sum('credit'))
        debit = qs['dr'] or Decimal('0')
        credit = qs['cr'] or Decimal('0')
        if debit or credit:
            rows.append({'account': acc, 'debit': debit, 'credit': credit})
    return rows
