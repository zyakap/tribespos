from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import TailoringOrder, TailoringStageLog


@transaction.atomic
def confirm_order(order: TailoringOrder, deposit_amount: Decimal, user=None):
    """Confirm order, reserve fabric stock, record deposit."""
    if order.status != 'quote':
        raise ValueError("Only quote orders can be confirmed.")

    # Reserve fabric stock
    if order.fabric_product and order.fabric_qty:
        from apps.warehouse.services import reserve_stock
        from apps.warehouse.models import Warehouse
        warehouse = Warehouse.objects.filter(is_active=True).first()
        if warehouse:
            reserve_stock(order.fabric_product, warehouse, order.fabric_qty)

    order.deposit_paid = deposit_amount
    order.balance_due = order.total - deposit_amount
    order.status = 'confirmed'
    order.save(update_fields=['deposit_paid', 'balance_due', 'status'])

    TailoringStageLog.objects.create(
        tailoring_order=order, stage='confirmed',
        notes=f'Deposit K{deposit_amount} received', changed_by=user
    )

    # Post deposit journal entry
    try:
        from apps.accounting.services import post_tailoring_deposit
        post_tailoring_deposit(order, deposit_amount, user)
    except Exception:
        pass


@transaction.atomic
def update_stage(order: TailoringOrder, new_stage: str, notes: str = '', user=None):
    """Progress order to next stage."""
    order.status = new_stage
    order.save(update_fields=['status'])
    TailoringStageLog.objects.create(
        tailoring_order=order, stage=new_stage, notes=notes, changed_by=user
    )


@transaction.atomic
def collect_order(order: TailoringOrder, balance_payment: Decimal, user=None):
    """Final collection: deduct fabric, post revenue journals."""
    if order.status not in ('ready', 'finishing'):
        raise ValueError("Order is not ready for collection.")

    # Unreserve and deduct fabric stock
    if order.fabric_product and order.fabric_qty:
        from apps.warehouse.services import unreserve_stock, adjust_stock
        from apps.warehouse.models import Warehouse
        warehouse = Warehouse.objects.filter(is_active=True).first()
        if warehouse:
            unreserve_stock(order.fabric_product, warehouse, order.fabric_qty)
            adjust_stock(
                order.fabric_product, warehouse, -order.fabric_qty,
                'production', reference_type='TailoringOrder', reference_id=order.id,
                unit_cost=order.fabric_product.cost_price, user=user
            )

    order.deposit_paid += balance_payment
    order.balance_due = Decimal('0')
    order.status = 'collected'
    order.collected_date = timezone.now().date()
    order.save(update_fields=['deposit_paid', 'balance_due', 'status', 'collected_date'])

    TailoringStageLog.objects.create(
        tailoring_order=order, stage='collected',
        notes=f'Balance K{balance_payment} collected', changed_by=user
    )

    # Post revenue journals
    try:
        from apps.accounting.services import post_tailoring_collection
        post_tailoring_collection(order, balance_payment, user)
    except Exception:
        pass
