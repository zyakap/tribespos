from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.floor_plan, name='floor_plan'),
    path('kitchen/', views.kitchen_display, name='kitchen'),
    path('table/<int:pk>/', views.table_detail, name='table_detail'),
]
