from django.contrib import admin
from .models import Warehouse, StockLocation, StockMovement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_unit', 'location_type', 'is_active']
    list_filter = ['business_unit', 'location_type', 'is_active']


@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'qty_on_hand', 'qty_reserved']
    list_filter = ['warehouse']
    search_fields = ['product__sku', 'product__name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'product', 'warehouse', 'movement_type', 'qty']
    list_filter = ['movement_type', 'warehouse']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['created_at']
