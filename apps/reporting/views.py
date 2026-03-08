from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta


@login_required
def dashboard(request):
    from apps.pos.models import SaleOrder, Payment
    from apps.products.models import Product
    from apps.tailoring.models import TailoringOrder
    from apps.warehouse.models import StockLocation
    from django.db.models import Sum, Count, F

    today = date.today()

    # Today's sales
    today_orders = SaleOrder.objects.filter(
        status='completed', completed_at__date=today
    )
    today_revenue = today_orders.aggregate(s=Sum('total'))['s'] or 0
    today_count = today_orders.count()

    # Sales by business unit
    unit_sales = today_orders.values(
        'business_unit__name', 'business_unit__unit_type'
    ).annotate(total=Sum('total'))

    # Low stock count
    low_stock_count = StockLocation.objects.filter(
        qty_on_hand__lte=F('product__min_stock_level'),
        product__track_inventory=True,
        product__is_active=True,
    ).exclude(product__min_stock_level=0).count()

    # Open tailoring orders
    open_tailoring = TailoringOrder.objects.filter(
        status__in=['confirmed', 'cutting', 'sewing', 'finishing', 'ready']
    ).count()

    # Recent orders
    recent_orders = SaleOrder.objects.filter(
        status='completed'
    ).select_related('business_unit', 'customer').order_by('-completed_at')[:10]

    return render(request, 'reporting/dashboard.html', {
        'today_revenue': today_revenue,
        'today_count': today_count,
        'unit_sales': unit_sales,
        'low_stock_count': low_stock_count,
        'open_tailoring': open_tailoring,
        'recent_orders': recent_orders,
        'today': today,
    })


@login_required
def daily_sales(request):
    from apps.pos.models import SaleOrder, Payment
    from django.db.models import Sum
    report_date = request.GET.get('date', str(date.today()))
    orders = SaleOrder.objects.filter(
        status='completed', completed_at__date=report_date
    ).select_related('business_unit', 'customer', 'cashier')
    total = orders.aggregate(s=Sum('total'))['s'] or 0
    return render(request, 'reporting/daily_sales.html', {
        'orders': orders, 'total': total, 'report_date': report_date
    })


@login_required
def z_report(request, session_id):
    from apps.pos.models import CashSession, SaleOrder, Payment
    from django.db.models import Sum
    session = CashSession.objects.get(pk=session_id)
    orders = SaleOrder.objects.filter(
        business_unit=session.business_unit,
        completed_at__gte=session.opened_at,
        status='completed',
    )
    payments = Payment.objects.filter(order__in=orders)
    payment_totals = payments.values('payment_method').annotate(total=Sum('amount'))
    return render(request, 'reporting/z_report.html', {
        'session': session, 'orders': orders, 'payment_totals': payment_totals
    })
