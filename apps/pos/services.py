from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import SaleOrder, Payment
from apps.warehouse.services import adjust_stock, deduct_bom_stock


@transaction.atomic
def complete_sale(order: SaleOrder, payments: list, user=None):
    """
    Complete a sale: deduct stock, post journal entries, record payments.
    payments: list of dicts with {payment_method, amount, tendered, reference}
    """
    if order.status != 'open':
        raise ValueError(f"Cannot complete order with status '{order.status}'")

    order.recalculate_totals()

    # Deduct stock
    for line in order.lines.select_related('product', 'variant').all():
        if line.product.track_inventory:
            _deduct_sale_stock(line, order, user)

    # Record payments
    total_paid = Decimal('0')
    for pdata in payments:
        p = Payment.objects.create(
            order=order,
            payment_method=pdata['payment_method'],
            amount=pdata['amount'],
            tendered=pdata.get('tendered'),
            change_given=pdata.get('change_given'),
            reference=pdata.get('reference', ''),
            processed_by=user,
        )
        total_paid += p.amount

    # Post accounting journal entry
    try:
        from apps.accounting.services import post_sale_journal
        post_sale_journal(order, payments)
    except Exception:
        pass  # Accounting is non-blocking for now

    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save(update_fields=['status', 'completed_at'])

    return order


def _deduct_sale_stock(line, order, user):
    from apps.products.models import Product
    product = line.product
    try:
        warehouse = order.business_unit.warehouses.filter(is_active=True).first()
        if not warehouse:
            return
        if product.product_type == 'composite':
            deduct_bom_stock(product, line.qty, warehouse, user)
        else:
            adjust_stock(
                product, warehouse, -line.qty, 'sale',
                reference_type='SaleOrder', reference_id=order.id,
                unit_cost=product.cost_price, user=user, variant=line.variant
            )
    except Exception:
        pass
