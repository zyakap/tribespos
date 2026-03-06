from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.products.models import Product
from apps.products.serializers import ProductSerializer, ProductListSerializer
from apps.warehouse.models import StockLocation
from apps.warehouse.serializers import StockLocationSerializer
from apps.pos.models import SaleOrder, CashSession
from apps.pos.serializers import SaleOrderSerializer, SaleOrderCreateSerializer
from apps.restaurant.models import RestaurantTable, KitchenTicket
from apps.restaurant.serializers import RestaurantTableSerializer, KitchenTicketSerializer
from apps.tailoring.models import TailoringOrder
from apps.tailoring.serializers import TailoringOrderSerializer
from apps.procurement.models import PurchaseOrder
from apps.procurement.serializers import PurchaseOrderSerializer
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierSerializer
from apps.accounting.models import Account
from apps.accounting.serializers import AccountSerializer
from apps.irc_tax.models import GSTReturn
from apps.irc_tax.serializers import GSTReturnSerializer


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        barcode = self.request.query_params.get('barcode')
        if barcode:
            qs = qs.filter(barcode=barcode)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(sku__icontains=search)
        return qs


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class ProductBarcodeAPIView(APIView):
    def get(self, request):
        barcode = request.query_params.get('barcode', '')
        try:
            product = Product.objects.get(barcode=barcode, is_active=True)
            return Response(ProductListSerializer(product).data)
        except Product.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class LowStockAPIView(generics.ListAPIView):
    serializer_class = StockLocationSerializer
    def get_queryset(self):
        from django.db.models import F
        return StockLocation.objects.filter(
            qty_on_hand__lte=F('product__min_stock_level'),
            product__track_inventory=True, product__is_active=True,
        ).exclude(product__min_stock_level=0).select_related('product', 'warehouse')


class SaleOrderListCreateAPIView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaleOrderCreateSerializer
        return SaleOrderSerializer
    def get_queryset(self):
        return SaleOrder.objects.filter(status__in=['open', 'held']).order_by('-opened_at')[:50]
    def perform_create(self, serializer):
        from apps.core.utils import generate_sequence_number
        order = serializer.save(
            order_number=generate_sequence_number(SaleOrder, 'SO', 'order_number'),
            cashier=self.request.user,
        )


class SaleOrderDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = SaleOrder.objects.all()
    serializer_class = SaleOrderSerializer


class PayOrderAPIView(APIView):
    def post(self, request, pk):
        order = get_object_or_404(SaleOrder, pk=pk)
        from apps.pos.services import complete_sale
        try:
            complete_sale(order, request.data.get('payments', []), user=request.user)
            return Response({'status': 'completed', 'order_number': order.order_number})
        except ValueError as e:
            return Response({'error': str(e)}, status=400)


class VoidOrderAPIView(APIView):
    def post(self, request, pk):
        order = get_object_or_404(SaleOrder, pk=pk)
        order.status = 'void'
        order.save(update_fields=['status'])
        return Response({'status': 'void'})


class OfflineSyncAPIView(APIView):
    def post(self, request):
        orders_data = request.data.get('orders', [])
        synced = []
        for order_data in orders_data:
            pass  # Process each offline order
        return Response({'synced': len(synced)})


class CurrentSessionAPIView(APIView):
    def get(self, request):
        session = CashSession.objects.filter(cashier=request.user, status='open').first()
        if session:
            return Response({'id': session.id, 'terminal_id': session.terminal_id, 'opened_at': str(session.opened_at)})
        return Response({'session': None})


class OpenSessionAPIView(APIView):
    def post(self, request):
        from apps.core.models import BusinessUnit
        unit_id = request.data.get('business_unit_id')
        unit = get_object_or_404(BusinessUnit, id=unit_id)
        session = CashSession.objects.create(
            terminal_id=request.data.get('terminal_id', 'POS-01'),
            cashier=request.user, business_unit=unit,
            opening_float=request.data.get('opening_float', 0),
        )
        return Response({'session_id': session.id})


class CloseSessionAPIView(APIView):
    def post(self, request):
        from django.utils import timezone
        session = CashSession.objects.filter(cashier=request.user, status='open').first()
        if session:
            session.closing_cash = request.data.get('closing_cash', 0)
            session.closed_at = timezone.now()
            session.status = 'closed'
            session.save()
        return Response({'status': 'closed'})


class TableListAPIView(generics.ListAPIView):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer


class KitchenTicketListAPIView(generics.ListAPIView):
    queryset = KitchenTicket.objects.filter(status__in=['new', 'acknowledged', 'preparing'])
    serializer_class = KitchenTicketSerializer


class KitchenTicketUpdateAPIView(generics.UpdateAPIView):
    queryset = KitchenTicket.objects.all()
    serializer_class = KitchenTicketSerializer


class TailoringOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = TailoringOrder.objects.all()
    serializer_class = TailoringOrderSerializer


class TailoringOrderDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = TailoringOrder.objects.all()
    serializer_class = TailoringOrderSerializer


class StockListAPIView(generics.ListAPIView):
    queryset = StockLocation.objects.select_related('product', 'warehouse').all()
    serializer_class = StockLocationSerializer


class StockAdjustAPIView(APIView):
    def post(self, request):
        from apps.warehouse.services import adjust_stock
        from apps.products.models import Product
        from apps.warehouse.models import Warehouse
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        warehouse = get_object_or_404(Warehouse, id=request.data.get('warehouse_id'))
        adjust_stock(product, warehouse, request.data.get('qty_delta', 0),
                     request.data.get('movement_type', 'adjustment'), user=request.user)
        return Response({'status': 'adjusted'})


class PurchaseOrderListAPIView(generics.ListAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class SupplierListAPIView(generics.ListAPIView):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer


class AccountListAPIView(generics.ListAPIView):
    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer


class PLReportAPIView(APIView):
    def get(self, request):
        from apps.accounting.reports import generate_pl
        from datetime import date
        today = date.today()
        start = date.fromisoformat(request.query_params.get('start', f'{today.year}-01-01'))
        end = date.fromisoformat(request.query_params.get('end', str(today)))
        pl = generate_pl(start, end)
        return Response({k: str(v) for k, v in pl.items()})


class TrialBalanceAPIView(APIView):
    def get(self, request):
        from apps.accounting.reports import generate_trial_balance
        rows = generate_trial_balance()
        return Response([{
            'account_code': r['account'].code,
            'account_name': r['account'].name,
            'debit': str(r['debit']),
            'credit': str(r['credit']),
        } for r in rows])


class GSTReturnListAPIView(generics.ListAPIView):
    queryset = GSTReturn.objects.all()
    serializer_class = GSTReturnSerializer


class GSTGenerateAPIView(APIView):
    def post(self, request):
        year = request.data.get('year')
        month = request.data.get('month')
        from apps.irc_tax.services.gst_service import generate_gst_return
        gst = generate_gst_return(int(year), int(month))
        return Response({'period': gst.return_period, 'status': gst.status})


class TaxCalendarAPIView(APIView):
    def get(self, request):
        from apps.irc_tax.utils import get_upcoming_tax_deadlines
        deadlines = get_upcoming_tax_deadlines(months_ahead=3)
        return Response([{**d, 'due_date': str(d['due_date'])} for d in deadlines])


class SWTCalculatorAPIView(APIView):
    def get(self, request):
        from apps.irc_tax.swt_tables import calculate_swt_with_benefits
        gross = float(request.query_params.get('gross', 0))
        resident = request.query_params.get('resident', 'true').lower() == 'true'
        result = calculate_swt_with_benefits(gross, is_resident=resident)
        return Response(result)
