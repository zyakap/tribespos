from django.contrib import admin
from .models import RestaurantTable, KitchenTicket


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'business_unit', 'section', 'capacity', 'status']
    list_filter = ['business_unit', 'status', 'section']


@admin.register(KitchenTicket)
class KitchenTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'order', 'status', 'created_at']
    list_filter = ['status']
