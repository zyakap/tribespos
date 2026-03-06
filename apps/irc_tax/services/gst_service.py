from decimal import Decimal
from django.db import transaction as db_transaction
from ..models import GSTReturn, GSTReturnLine


def generate_gst_return(year: int, month: int) -> GSTReturn:
    import calendar
    from datetime import date
    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    if month == 12:
        due_date = date(year + 1, 1, 21)
    else:
        due_date = date(year, month + 1, 21)

    with db_transaction.atomic():
        gst_return, created = GSTReturn.objects.get_or_create(
            return_period=f"{year:04d}-{month:02d}",
            defaults={'period_start': period_start, 'period_end': period_end, 'due_date': due_date, 'status': 'draft'},
        )
        if gst_return.status == 'draft':
            gst_return.lines.all().delete()
            _calculate_output_tax(gst_return, period_start, period_end)
            _calculate_input_tax(gst_return, period_start, period_end)
            _update_return_totals(gst_return)
    return gst_return


def _calculate_output_tax(gst_return, start, end):
    from apps.pos.models import SaleOrder
    sales = SaleOrder.objects.filter(status='completed', completed_at__date__gte=start, completed_at__date__lte=end)
    for order in sales:
        for line in order.lines.select_related('product').all():
            supply_type = getattr(line.product, 'gst_supply_type', 'T')
            if supply_type == 'T':
                if line.product.tax_inclusive:
                    gst_excl = line.line_total / Decimal('1.10')
                    gst_amt = line.line_total - gst_excl
                else:
                    gst_excl = line.line_total
                    gst_amt = line.line_total * Decimal('0.10')
            else:
                gst_excl = line.line_total
                gst_amt = Decimal('0.00')
            GSTReturnLine.objects.create(
                gst_return=gst_return, line_type='output', transaction_type='sale',
                reference_type='SaleOrder', reference_id=order.id,
                transaction_date=order.completed_at.date(),
                supplier_customer=order.customer.name if order.customer else 'Walk-in',
                description=f"Sale {order.order_number}",
                gst_exclusive_amount=gst_excl.quantize(Decimal('0.01')),
                gst_amount=gst_amt.quantize(Decimal('0.01')),
                supply_type=supply_type,
            )


def _calculate_input_tax(gst_return, start, end):
    from apps.procurement.models import SupplierInvoice
    invoices = SupplierInvoice.objects.filter(
        invoice_date__gte=start, invoice_date__lte=end, status__in=['unpaid', 'partial', 'paid']
    ).select_related('supplier')
    for inv in invoices:
        GSTReturnLine.objects.create(
            gst_return=gst_return, line_type='input', transaction_type='purchase_invoice',
            reference_type='SupplierInvoice', reference_id=inv.id,
            transaction_date=inv.invoice_date, supplier_customer=inv.supplier.name,
            description=f"Invoice {inv.invoice_number}",
            gst_exclusive_amount=inv.subtotal, gst_amount=inv.tax_total, supply_type='T',
        )


def _update_return_totals(gst_return):
    from django.db.models import Sum
    lines = gst_return.lines.all()
    output = lines.filter(line_type='output')
    inputs = lines.filter(line_type='input')
    gst_return.total_taxable_sales = output.filter(supply_type='T').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.total_zero_rated_sales = output.filter(supply_type='Z').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.total_exempt_sales = output.filter(supply_type='E').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.output_tax_collected = output.aggregate(s=Sum('gst_amount'))['s'] or 0
    gst_return.total_taxable_purchases = inputs.aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.input_tax_credits = inputs.aggregate(s=Sum('gst_amount'))['s'] or 0
    net = gst_return.output_tax_collected - gst_return.input_tax_credits
    gst_return.net_gst_payable = max(net, Decimal('0.00'))
    gst_return.net_gst_refundable = max(-net, Decimal('0.00'))
    gst_return.total_gross_sales = (
        gst_return.total_taxable_sales + gst_return.total_zero_rated_sales + gst_return.total_exempt_sales
    )
    gst_return.save()
