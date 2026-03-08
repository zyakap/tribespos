from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderLine, GoodsReceivedNote, GRNLine, SupplierInvoice


class POLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLine
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines = POLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class SupplierInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierInvoice
        fields = '__all__'
