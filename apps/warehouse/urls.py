from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.stock_dashboard, name='stock_dashboard'),
    path('adjust/', views.stock_adjust, name='adjust'),
    path('movements/', views.movement_list, name='movement_list'),
]
