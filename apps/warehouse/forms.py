from django import forms
from .models import StockMovement


class StockAdjustmentForm(forms.Form):
    ADJUSTMENT_TYPES = [
        ('adjustment', 'Adjustment'),
        ('waste', 'Waste / Write-off'),
        ('return', 'Return'),
    ]
    from apps.products.models import Product
    from .models import Warehouse

    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True, track_inventory=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    qty_delta = forms.DecimalField(max_digits=12, decimal_places=3, help_text='Positive=add, Negative=remove')
    movement_type = forms.ChoiceField(choices=ADJUSTMENT_TYPES)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
