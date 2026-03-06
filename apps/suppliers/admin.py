from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'phone', 'payment_terms', 'is_active']
    list_filter = ['currency', 'is_active']
    search_fields = ['code', 'name', 'contact_person', 'email']
