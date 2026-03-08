from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_terminal, name='terminal'),
    path('<str:unit_code>/', views.pos_terminal, name='terminal_unit'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/receipt/', views.receipt_view, name='receipt'),
    path('session/open/', views.open_session, name='open_session'),
]
