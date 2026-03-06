from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.journal_list, name='journal_list'),
    path('journal/<int:pk>/', views.journal_detail, name='journal_detail'),
    path('coa/', views.coa_list, name='coa_list'),
    path('reports/pl/', views.pl_report, name='pl_report'),
    path('reports/trial-balance/', views.trial_balance, name='trial_balance'),
]
