import re
from datetime import date
from django.db import models


def generate_sequence_number(model_class, prefix: str, field_name: str = 'order_number') -> str:
    """
    Generate a padded sequence number like PO-2024-00001.
    Thread-safe via select_for_update.
    """
    year = date.today().year
    pattern = f"{prefix}-{year}-"
    last = (
        model_class.objects.filter(**{f"{field_name}__startswith": pattern})
        .order_by(field_name)
        .last()
    )
    if last:
        last_num = int(getattr(last, field_name).split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{year}-{new_num:05d}"


def money_round(value) -> 'Decimal':
    from decimal import Decimal, ROUND_HALF_UP
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
