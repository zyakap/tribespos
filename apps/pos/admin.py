from django.contrib import admin
from .models import CashSession, SaleOrder, SaleOrderLine, Payment


class SaleOrderLineInline(admin.TabularInline):
    model = SaleOrderLine
    extra = 0
    readonly_fields = ['line_total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['paid_at']


@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'business_unit', 'sale_type', 'status', 'total', 'opened_at']
    list_filter = ['status', 'sale_type', 'business_unit']
    search_fields = ['order_number', 'customer__name']
    readonly_fields = ['order_number', 'opened_at', 'completed_at']
    inlines = [SaleOrderLineInline, PaymentInline]


@admin.register(CashSession)
class CashSessionAdmin(admin.ModelAdmin):
    list_display = ['terminal_id', 'cashier', 'business_unit', 'opened_at', 'status', 'variance']
    list_filter = ['status', 'business_unit']
