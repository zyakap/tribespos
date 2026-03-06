from django.contrib import admin
from .models import Category, UnitOfMeasure, Product, ProductVariant, BOMItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'business_unit', 'sort_order']
    list_filter = ['business_unit']


@admin.register(UnitOfMeasure)
class UOMAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class BOMItemInline(admin.TabularInline):
    model = BOMItem
    fk_name = 'parent_product'
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'product_type', 'sell_price', 'track_inventory', 'is_active']
    list_filter = ['product_type', 'category', 'gst_supply_type', 'is_active']
    search_fields = ['sku', 'barcode', 'name']
    inlines = [ProductVariantInline, BOMItemInline]
