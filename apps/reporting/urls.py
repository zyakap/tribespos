from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('daily-sales/', views.daily_sales, name='daily_sales'),
    path('z-report/<int:session_id>/', views.z_report, name='z_report'),
]
