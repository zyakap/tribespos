from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import TailoringOrder
from .forms import TailoringOrderForm, DepositForm, CollectionForm
from .services import confirm_order, update_stage, collect_order
from apps.core.utils import generate_sequence_number


@login_required
def order_list(request):
    qs = TailoringOrder.objects.select_related('customer', 'tailor').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'tailoring/list.html', {'page_obj': page, 'status': status})


@login_required
def order_create(request):
    form = TailoringOrderForm(request.POST or None)
    if form.is_valid():
        order = form.save(commit=False)
        order.order_number = generate_sequence_number(TailoringOrder, 'TAIL')
        order.created_by = request.user
        order.save()
        order.recalculate_total()
        messages.success(request, f'Order {order.order_number} created.')
        return redirect('tailoring:detail', pk=order.pk)
    return render(request, 'tailoring/form.html', {'form': form, 'title': 'New Tailoring Order'})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(TailoringOrder, pk=pk)
    deposit_form = DepositForm()
    collection_form = CollectionForm()
    return render(request, 'tailoring/detail.html', {
        'order': order, 'deposit_form': deposit_form, 'collection_form': collection_form
    })


@login_required
def order_confirm(request, pk):
    order = get_object_or_404(TailoringOrder, pk=pk)
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            confirm_order(order, form.cleaned_data['deposit_amount'], user=request.user)
            messages.success(request, 'Order confirmed and deposit recorded.')
    return redirect('tailoring:detail', pk=pk)


@login_required
def order_stage_update(request, pk):
    order = get_object_or_404(TailoringOrder, pk=pk)
    if request.method == 'POST':
        new_stage = request.POST.get('stage')
        notes = request.POST.get('notes', '')
        update_stage(order, new_stage, notes, user=request.user)
        messages.success(request, f'Stage updated to {new_stage}.')
    return redirect('tailoring:detail', pk=pk)


@login_required
def order_collect(request, pk):
    order = get_object_or_404(TailoringOrder, pk=pk)
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            try:
                collect_order(order, form.cleaned_data['balance_payment'], user=request.user)
                messages.success(request, 'Order collected and payment recorded.')
            except ValueError as e:
                messages.error(request, str(e))
    return redirect('tailoring:detail', pk=pk)
