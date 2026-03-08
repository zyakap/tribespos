from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import StockLocation, StockMovement, Warehouse
from .services import adjust_stock
from .forms import StockAdjustmentForm


@login_required
def stock_dashboard(request):
    warehouses = Warehouse.objects.filter(is_active=True)
    warehouse_id = request.GET.get('warehouse', '')
    qs = StockLocation.objects.filter(product__is_active=True).select_related('product', 'warehouse', 'product__category')
    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)
    paginator = Paginator(qs.order_by('product__name'), 50)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'warehouse/stock_dashboard.html', {
        'page_obj': page, 'warehouses': warehouses, 'selected_warehouse': warehouse_id
    })


@login_required
def stock_adjust(request):
    form = StockAdjustmentForm(request.POST or None)
    if form.is_valid():
        d = form.cleaned_data
        adjust_stock(
            d['product'], d['warehouse'], d['qty_delta'],
            d['movement_type'], notes=d.get('notes', ''), user=request.user
        )
        messages.success(request, 'Stock adjusted successfully.')
        return redirect('warehouse:stock_dashboard')
    return render(request, 'warehouse/adjust.html', {'form': form})


@login_required
def movement_list(request):
    qs = StockMovement.objects.select_related('product', 'warehouse').order_by('-created_at')
    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'warehouse/movement_list.html', {'page_obj': page})
