from django import forms
from .models import Product, ProductVariant, BOMItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'barcode', 'name', 'category', 'uom', 'product_type',
            'cost_price', 'sell_price', 'sell_price_wholesale',
            'tax_rate', 'tax_inclusive', 'gst_supply_type',
            'track_inventory', 'min_stock_level', 'reorder_qty',
            'image', 'description',
        ]
