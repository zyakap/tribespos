from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import PurchaseOrder, GoodsReceivedNote, SupplierInvoice
from .services import post_grn


@login_required
def po_list(request):
    qs = PurchaseOrder.objects.select_related('supplier', 'warehouse').order_by('-order_date')
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'procurement/po_list.html', {'page_obj': page})


@login_required
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'procurement/po_detail.html', {'po': po})


@login_required
def grn_create(request, po_pk):
    po = get_object_or_404(PurchaseOrder, pk=po_pk)
    return render(request, 'procurement/grn_form.html', {'po': po})


@login_required
def grn_post(request, pk):
    grn = get_object_or_404(GoodsReceivedNote, pk=pk)
    try:
        post_grn(grn, user=request.user)
        messages.success(request, f'GRN {grn.grn_number} posted successfully.')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('procurement:po_detail', pk=grn.po_id)


@login_required
def invoice_list(request):
    qs = SupplierInvoice.objects.select_related('supplier').order_by('-invoice_date')
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'procurement/invoice_list.html', {'page_obj': page})
