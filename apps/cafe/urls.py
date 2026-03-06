from django.urls import path
from . import views

app_name = 'cafe'

urlpatterns = [
    path('', views.cafe_pos, name='pos'),
]
