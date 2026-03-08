from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Supplier
from .forms import SupplierForm


@login_required
def supplier_list(request):
    qs = Supplier.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'suppliers/list.html', {'page_obj': page, 'q': q})


@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('suppliers:list')
    return render(request, 'suppliers/form.html', {'form': form, 'title': 'New Supplier'})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'suppliers/detail.html', {'supplier': supplier})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        return redirect('suppliers:detail', pk=pk)
    return render(request, 'suppliers/form.html', {'form': form, 'title': 'Edit Supplier'})
