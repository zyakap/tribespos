from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import SaleOrder, CashSession
from .services import complete_sale
from apps.core.models import BusinessUnit
from apps.products.models import Product, Category


@login_required
def pos_terminal(request, unit_code=None):
    if unit_code:
        unit = get_object_or_404(BusinessUnit, code=unit_code, is_active=True)
    else:
        unit = BusinessUnit.objects.filter(is_active=True).first()
    categories = Category.objects.filter(business_unit=unit).order_by('sort_order')
    session = CashSession.objects.filter(
        cashier=request.user, business_unit=unit, status='open'
    ).first()
    return render(request, 'pos/terminal.html', {
        'unit': unit, 'categories': categories, 'session': session
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(SaleOrder, pk=pk)
    return render(request, 'pos/order_detail.html', {'order': order})


@login_required
@require_POST
def open_session(request):
    data = json.loads(request.body)
    unit = get_object_or_404(BusinessUnit, id=data.get('business_unit_id'))
    session = CashSession.objects.create(
        terminal_id=data.get('terminal_id', 'POS-01'),
        cashier=request.user,
        business_unit=unit,
        opening_float=data.get('opening_float', 0),
    )
    return JsonResponse({'session_id': session.id, 'opened_at': str(session.opened_at)})


@login_required
def receipt_view(request, pk):
    order = get_object_or_404(SaleOrder, pk=pk)
    return render(request, 'pos/receipt.html', {'order': order})
