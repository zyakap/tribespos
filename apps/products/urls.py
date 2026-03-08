from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('new/', views.product_create, name='create'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('low-stock/', views.product_low_stock, name='low_stock'),
    path('barcode-lookup/', views.product_barcode_lookup, name='barcode_lookup'),
]
