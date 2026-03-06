from decimal import Decimal
from django.db import transaction
from .models import StockLocation, StockMovement, Warehouse
from apps.products.models import Product, ProductVariant


def get_or_create_stock_location(product, warehouse, variant=None):
    loc, _ = StockLocation.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        variant=variant,
    )
    return loc


@transaction.atomic
def adjust_stock(product, warehouse, qty_delta, movement_type, reference_type='',
                 reference_id=None, unit_cost=None, notes='', user=None, variant=None):
    """
    Adjust stock for a product in a warehouse.
    qty_delta: positive = increase, negative = decrease.
    """
    loc = get_or_create_stock_location(product, warehouse, variant)
    loc.qty_on_hand = loc.qty_on_hand + Decimal(str(qty_delta))
    loc.save(update_fields=['qty_on_hand'])

    total_cost = None
    if unit_cost is not None:
        total_cost = abs(Decimal(str(qty_delta))) * Decimal(str(unit_cost))

    StockMovement.objects.create(
        product=product,
        variant=variant,
        warehouse=warehouse,
        movement_type=movement_type,
        reference_type=reference_type,
        reference_id=reference_id,
        qty=Decimal(str(qty_delta)),
        unit_cost=unit_cost,
        total_cost=total_cost,
        notes=notes,
        created_by=user,
    )


@transaction.atomic
def transfer_stock(product, from_warehouse, to_warehouse, qty, user=None, variant=None, notes=''):
    """Transfer stock between warehouses."""
    adjust_stock(product, from_warehouse, -qty, 'transfer_out', notes=notes, user=user, variant=variant)
    adjust_stock(product, to_warehouse, qty, 'transfer_in', notes=notes, user=user, variant=variant)


@transaction.atomic
def reserve_stock(product, warehouse, qty, variant=None):
    """Reserve stock (e.g. for tailoring orders)."""
    loc = get_or_create_stock_location(product, warehouse, variant)
    loc.qty_reserved = loc.qty_reserved + Decimal(str(qty))
    loc.save(update_fields=['qty_reserved'])


@transaction.atomic
def unreserve_stock(product, warehouse, qty, variant=None):
    loc = get_or_create_stock_location(product, warehouse, variant)
    loc.qty_reserved = max(loc.qty_reserved - Decimal(str(qty)), Decimal('0'))
    loc.save(update_fields=['qty_reserved'])


def deduct_bom_stock(product, qty_sold, warehouse, user=None):
    """For composite products, deduct each BOM component from stock."""
    for bom_item in product.bom_items.select_related('component_product').all():
        component_qty = bom_item.quantity * Decimal(str(qty_sold))
        adjust_stock(
            bom_item.component_product, warehouse, -component_qty,
            'sale', 'Product', product.id, user=user
        )
