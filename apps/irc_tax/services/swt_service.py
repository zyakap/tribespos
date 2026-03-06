from django.db.models import Sum, Count
from ..models import SWTRemittance, PayrollRun


def generate_swt_remittance(year: int, month: int) -> SWTRemittance:
    from datetime import date
    import calendar
    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    if month == 12:
        due_date = date(year + 1, 1, 7)
    else:
        due_date = date(year, month + 1, 7)

    runs = PayrollRun.objects.filter(
        status='paid', pay_period_start__gte=period_start, pay_period_end__lte=period_end
    )
    totals = runs.aggregate(gross=Sum('total_gross'), swt=Sum('total_swt'))

    remittance, _ = SWTRemittance.objects.update_or_create(
        remittance_month=f"{year:04d}-{month:02d}",
        defaults={
            'due_date': due_date,
            'period_start': period_start,
            'period_end': period_end,
            'total_gross_wages': totals['gross'] or 0,
            'total_swt_withheld': totals['swt'] or 0,
            'status': 'draft',
        }
    )
    return remittance
