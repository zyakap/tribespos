from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import RestaurantTable, KitchenTicket
from apps.core.models import BusinessUnit


@login_required
def floor_plan(request):
    unit = BusinessUnit.objects.filter(unit_type='restaurant', is_active=True).first()
    tables = RestaurantTable.objects.filter(business_unit=unit).order_by('table_number')
    return render(request, 'restaurant/floor_plan.html', {'tables': tables, 'unit': unit})


@login_required
def kitchen_display(request):
    tickets = KitchenTicket.objects.filter(status__in=['new', 'acknowledged', 'preparing']).select_related('order')
    return render(request, 'restaurant/kitchen_display.html', {'tickets': tickets})


@login_required
def table_detail(request, pk):
    table = get_object_or_404(RestaurantTable, pk=pk)
    return render(request, 'restaurant/table_detail.html', {'table': table})
