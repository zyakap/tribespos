from django.contrib import admin
from .models import BusinessUnit


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'unit_type', 'is_active']
    list_filter = ['unit_type', 'is_active']
    search_fields = ['code', 'name']
