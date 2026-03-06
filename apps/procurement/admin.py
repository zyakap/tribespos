from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderLine, GoodsReceivedNote, GRNLine, SupplierInvoice


class POLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'status', 'order_date', 'total']
    list_filter = ['status', 'supplier']
    search_fields = ['po_number', 'supplier__name']
    inlines = [POLineInline]


class GRNLineInline(admin.TabularInline):
    model = GRNLine
    extra = 1


@admin.register(GoodsReceivedNote)
class GRNAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'po', 'warehouse', 'received_date', 'is_posted']
    list_filter = ['is_posted', 'warehouse']
    inlines = [GRNLineInline]


@admin.register(SupplierInvoice)
class SupplierInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'total', 'amount_paid', 'status']
    list_filter = ['status', 'supplier']
