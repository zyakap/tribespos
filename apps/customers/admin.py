from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'customer_type', 'phone', 'outstanding_balance', 'is_active']
    list_filter = ['customer_type', 'is_active']
    search_fields = ['code', 'name', 'phone', 'email']
