from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def pgk(value):
    """Format value as PGK currency."""
    try:
        return f"K {Decimal(str(value)):,.2f}"
    except Exception:
        return value


@register.filter
def abs_value(value):
    try:
        return abs(value)
    except Exception:
        return value
