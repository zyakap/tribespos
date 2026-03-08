from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pin-login/', views.pin_login_view, name='pin_login'),
    path('profile/', views.profile_view, name='profile'),
]
