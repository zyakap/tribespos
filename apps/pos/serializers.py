from rest_framework import serializers
from .models import SaleOrder, SaleOrderLine, Payment, CashSession, OrderLineModifier


class OrderLineModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineModifier
        fields = ['id', 'modifier_name', 'price_adjustment']


class SaleOrderLineSerializer(serializers.ModelSerializer):
    modifiers = OrderLineModifierSerializer(many=True, read_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = SaleOrderLine
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class SaleOrderSerializer(serializers.ModelSerializer):
    lines = SaleOrderLineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = SaleOrder
        fields = '__all__'


class SaleOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrder
        fields = ['business_unit', 'customer', 'sale_type', 'table_number', 'terminal_id', 'notes']
