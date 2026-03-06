from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.po_list, name='po_list'),
    path('<int:pk>/', views.po_detail, name='po_detail'),
    path('<int:po_pk>/grn/', views.grn_create, name='grn_create'),
    path('grn/<int:pk>/post/', views.grn_post, name='grn_post'),
    path('invoices/', views.invoice_list, name='invoice_list'),
]
