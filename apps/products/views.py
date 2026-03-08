from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm


@login_required
def product_list(request):
    qs = Product.objects.filter(is_active=True).select_related('category', 'uom')
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q) | qs.filter(barcode__icontains=q)
    if category_id:
        qs = qs.filter(category_id=category_id)
    categories = Category.objects.all()
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'products/list.html', {'page_obj': page, 'q': q, 'categories': categories})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('products:list')
    return render(request, 'products/form.html', {'form': form, 'title': 'New Product'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('products:detail', pk=pk)
    return render(request, 'products/form.html', {'form': form, 'title': 'Edit Product'})


@login_required
def product_low_stock(request):
    from apps.warehouse.models import StockLocation
    from django.db.models import F
    low_stock = StockLocation.objects.filter(
        qty_on_hand__lte=F('product__min_stock_level'),
        product__track_inventory=True,
        product__is_active=True,
    ).select_related('product', 'warehouse').exclude(product__min_stock_level=0)
    return render(request, 'products/low_stock.html', {'low_stock': low_stock})


def product_barcode_lookup(request):
    barcode = request.GET.get('barcode', '')
    try:
        product = Product.objects.get(barcode=barcode, is_active=True)
        return JsonResponse({'id': product.id, 'sku': product.sku, 'name': product.name, 'sell_price': str(product.sell_price)})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
