"""
Harhurum POS — Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.reporting.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('customers/', include('apps.customers.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('products/', include('apps.products.urls')),
    path('warehouse/', include('apps.warehouse.urls')),
    path('procurement/', include('apps.procurement.urls')),
    path('pos/', include('apps.pos.urls')),
    path('cafe/', include('apps.cafe.urls')),
    path('restaurant/', include('apps.restaurant.urls')),
    path('tailoring/', include('apps.tailoring.urls')),
    path('accounting/', include('apps.accounting.urls')),
    path('tax/', include('apps.irc_tax.urls')),
    path('api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
