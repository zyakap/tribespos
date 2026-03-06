from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Customer
from .forms import CustomerForm


@login_required
def customer_list(request):
    qs = Customer.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'customers/list.html', {'page_obj': page, 'q': q})


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('customers:list')
    return render(request, 'customers/form.html', {'form': form, 'title': 'New Customer'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/detail.html', {'customer': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customers:detail', pk=pk)
    return render(request, 'customers/form.html', {'form': form, 'title': 'Edit Customer'})
