from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import GoodsReceivedNote, GRNLine, PurchaseOrder
from apps.warehouse.services import adjust_stock


@transaction.atomic
def post_grn(grn: GoodsReceivedNote, user=None):
    """
    Post a GRN: update stock, update weighted average cost, create journal entry.
    """
    if grn.is_posted:
        raise ValueError("GRN is already posted.")

    for line in grn.lines.select_related('product', 'variant').all():
        product = line.product
        adjust_stock(
            product=product,
            warehouse=grn.warehouse,
            qty_delta=line.qty_received,
            movement_type='purchase',
            reference_type='GoodsReceivedNote',
            reference_id=grn.id,
            unit_cost=line.unit_cost,
            user=user,
            variant=line.variant,
        )
        # Update qty_received on PO line
        line.po_line.qty_received += line.qty_received
        line.po_line.save(update_fields=['qty_received'])

        # Update weighted average cost
        _update_weighted_average_cost(product, line.qty_received, line.unit_cost)

    grn.is_posted = True
    grn.save(update_fields=['is_posted'])

    # Update PO status
    po = grn.po
    all_received = all(
        l.qty_received >= l.qty_ordered for l in po.lines.all()
    )
    po.status = 'received' if all_received else 'partial'
    po.received_date = timezone.now().date()
    po.save(update_fields=['status', 'received_date'])


def _update_weighted_average_cost(product, qty_received, unit_cost):
    """Recalculate weighted average cost after receiving stock."""
    from apps.warehouse.models import StockLocation
    from django.db.models import Sum

    total_qty = StockLocation.objects.filter(product=product).aggregate(
        t=Sum('qty_on_hand')
    )['t'] or Decimal('0')

    if total_qty > 0:
        old_qty = total_qty - qty_received
        new_cost = (
            (old_qty * product.cost_price + qty_received * unit_cost) / total_qty
        )
        product.cost_price = new_cost.quantize(Decimal('0.0001'))
        product.save(update_fields=['cost_price'])
