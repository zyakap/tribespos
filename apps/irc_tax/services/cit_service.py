from decimal import Decimal
from ..models import CITReturn, ProvisionalTaxInstalment


def generate_cit_return(tax_year: int) -> CITReturn:
    from apps.accounting.reports import generate_pl
    from datetime import date
    pl = generate_pl(start=date(tax_year, 1, 1), end=date(tax_year, 12, 31))
    total_revenue = pl['total_revenue']
    total_cogs = pl['total_cogs']
    total_expenses = pl['total_expenses']
    depreciation = pl['depreciation']
    assessable_income = total_revenue
    total_deductions = total_cogs + total_expenses
    taxable_income = max(assessable_income - total_deductions, Decimal('0'))
    gross_cit = taxable_income * Decimal('0.30')
    provisional_paid = ProvisionalTaxInstalment.objects.filter(
        tax_year=tax_year, status='paid'
    ).aggregate(s=sum('amount_paid'))['s'] or 0
    net_cit = max(gross_cit - Decimal(str(provisional_paid)), Decimal('0'))
    cit, _ = CITReturn.objects.update_or_create(
        tax_year=tax_year,
        defaults={
            'due_date': date(tax_year + 1, 4, 30),
            'total_revenue': total_revenue, 'assessable_income': assessable_income,
            'cogs': total_cogs, 'operating_expenses': total_expenses,
            'depreciation': depreciation, 'total_deductions': total_deductions,
            'taxable_income': taxable_income, 'gross_cit': gross_cit,
            'provisional_tax_paid': provisional_paid, 'net_cit_payable': net_cit,
        }
    )
    return cit


def create_provisional_instalments(tax_year: int, prior_year_cit: Decimal):
    from datetime import date
    quarters = [
        (1, date(tax_year, 3, 31)),
        (2, date(tax_year, 6, 30)),
        (3, date(tax_year, 9, 30)),
        (4, date(tax_year, 12, 31)),
    ]
    instalment_amount = (prior_year_cit / 4).quantize(Decimal('0.01'))
    for quarter, due_date in quarters:
        ProvisionalTaxInstalment.objects.get_or_create(
            tax_year=tax_year, quarter=quarter,
            defaults={'due_date': due_date, 'estimated_amount': instalment_amount, 'status': 'pending'}
        )
