from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.products.serializers import ProductListSerializer
from . import views

router = DefaultRouter()

urlpatterns = [
    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Products
    path('products/', views.ProductListAPIView.as_view(), name='api_products'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('products/barcode/', views.ProductBarcodeAPIView.as_view(), name='api_barcode'),
    path('products/low-stock/', views.LowStockAPIView.as_view(), name='api_low_stock'),

    # POS / Orders
    path('pos/orders/', views.SaleOrderListCreateAPIView.as_view(), name='api_orders'),
    path('pos/orders/<int:pk>/', views.SaleOrderDetailAPIView.as_view(), name='api_order_detail'),
    path('pos/orders/<int:pk>/pay/', views.PayOrderAPIView.as_view(), name='api_pay_order'),
    path('pos/orders/<int:pk>/void/', views.VoidOrderAPIView.as_view(), name='api_void_order'),
    path('pos/sync/', views.OfflineSyncAPIView.as_view(), name='api_pos_sync'),
    path('pos/sessions/current/', views.CurrentSessionAPIView.as_view(), name='api_session_current'),
    path('pos/sessions/open/', views.OpenSessionAPIView.as_view(), name='api_session_open'),
    path('pos/sessions/close/', views.CloseSessionAPIView.as_view(), name='api_session_close'),

    # Restaurant
    path('restaurant/tables/', views.TableListAPIView.as_view(), name='api_tables'),
    path('kitchen/tickets/', views.KitchenTicketListAPIView.as_view(), name='api_kitchen'),
    path('kitchen/tickets/<int:pk>/', views.KitchenTicketUpdateAPIView.as_view(), name='api_kitchen_ticket'),

    # Tailoring
    path('tailoring/orders/', views.TailoringOrderListCreateAPIView.as_view(), name='api_tailoring'),
    path('tailoring/orders/<int:pk>/', views.TailoringOrderDetailAPIView.as_view(), name='api_tailoring_detail'),

    # Stock
    path('stock/', views.StockListAPIView.as_view(), name='api_stock'),
    path('stock/adjust/', views.StockAdjustAPIView.as_view(), name='api_stock_adjust'),

    # Procurement
    path('purchase-orders/', views.PurchaseOrderListAPIView.as_view(), name='api_pos'),
    path('suppliers/', views.SupplierListAPIView.as_view(), name='api_suppliers'),

    # Accounting
    path('accounts/', views.AccountListAPIView.as_view(), name='api_accounts'),
    path('reports/pl/', views.PLReportAPIView.as_view(), name='api_pl'),
    path('reports/trial-balance/', views.TrialBalanceAPIView.as_view(), name='api_trial_balance'),

    # Tax
    path('tax/gst/', views.GSTReturnListAPIView.as_view(), name='api_gst_list'),
    path('tax/gst/generate/', views.GSTGenerateAPIView.as_view(), name='api_gst_generate'),
    path('tax/calendar/', views.TaxCalendarAPIView.as_view(), name='api_tax_calendar'),

    # Payroll
    path('payroll/swt-calculator/', views.SWTCalculatorAPIView.as_view(), name='api_swt_calc'),

    path('', include(router.urls)),
]
