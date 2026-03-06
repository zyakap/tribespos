from django.urls import path
from . import views

app_name = 'tailoring'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('new/', views.order_create, name='create'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/confirm/', views.order_confirm, name='confirm'),
    path('<int:pk>/stage/', views.order_stage_update, name='stage_update'),
    path('<int:pk>/collect/', views.order_collect, name='collect'),
]
