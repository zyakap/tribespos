from decimal import Decimal
from ..models import WithholdingTaxTransaction

WHT_RATES = {
    'dividend_resident': Decimal('17.0'),
    'dividend_non_resident': Decimal('15.0'),
    'interest': Decimal('15.0'),
    'royalty': Decimal('10.0'),
    'management_fee': Decimal('17.0'),
}


def record_wht(wht_type, payment_date, payee_name, payee_tin, payee_residence,
               gross_amount, override_rate=None) -> WithholdingTaxTransaction:
    gross = Decimal(str(gross_amount))
    if override_rate is not None:
        rate = Decimal(str(override_rate))
    else:
        rate_key = f"{wht_type}_{payee_residence}" if wht_type == 'dividend' else wht_type
        rate = WHT_RATES.get(rate_key, Decimal('15.0'))
    wht_amount = (gross * rate / 100).quantize(Decimal('0.01'))
    net_paid = gross - wht_amount
    return WithholdingTaxTransaction.objects.create(
        wht_type=wht_type, payment_date=payment_date,
        payee_name=payee_name, payee_tin=payee_tin,
        payee_residence=payee_residence, gross_amount=gross,
        wht_rate=rate, wht_amount=wht_amount, net_paid=net_paid,
    )
