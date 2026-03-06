from django.contrib import admin
from .models import TailoringOrder, TailoringStageLog


class StageLogInline(admin.TabularInline):
    model = TailoringStageLog
    extra = 0
    readonly_fields = ['created_at', 'changed_by']


@admin.register(TailoringOrder)
class TailoringOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'garment_type', 'total', 'promised_date']
    list_filter = ['status', 'tailor']
    search_fields = ['order_number', 'customer__name', 'garment_type']
    readonly_fields = ['order_number', 'created_at']
    inlines = [StageLogInline]
