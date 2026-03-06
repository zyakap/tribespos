from rest_framework import serializers
from .models import Category, UnitOfMeasure, Product, ProductVariant, BOMItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'


class BOMItemSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='component_product.name', read_only=True)

    class Meta:
        model = BOMItem
        fields = ['id', 'component_product', 'component_name', 'quantity']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    bom_items = BOMItemSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    uom_abbr = serializers.CharField(source='uom.abbreviation', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for POS product grid."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'sku', 'barcode', 'name', 'category_name', 'sell_price', 'tax_rate', 'tax_inclusive', 'product_type', 'image']
