from django.urls import path
from . import views

app_name = 'irc_tax'

urlpatterns = [
    path('', views.tax_dashboard, name='dashboard'),
    path('gst/', views.gst_return_list, name='gst_list'),
    path('gst/generate/', views.gst_generate, name='gst_generate'),
    path('gst/<str:period>/', views.gst_return_detail, name='gst_detail'),
    path('swt/', views.swt_list, name='swt_list'),
    path('cit/', views.cit_return, name='cit_return'),
    path('cit/<int:year>/', views.cit_return, name='cit_return_year'),
]
