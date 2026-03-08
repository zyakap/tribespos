from django import forms
from .models import TailoringOrder

MEASUREMENT_FIELDS = [
    'neck', 'chest', 'waist', 'hips', 'shoulder_width',
    'sleeve_length', 'back_length', 'inseam', 'outseam', 'thigh', 'knee', 'ankle'
]


class TailoringOrderForm(forms.ModelForm):
    class Meta:
        model = TailoringOrder
        fields = [
            'customer', 'tailor', 'garment_type', 'style_notes',
            'fabric_product', 'fabric_qty',
            'labour_charge', 'fabric_charge', 'additional_charge', 'discount_amount',
            'promised_date', 'notes',
        ]
        widgets = {
            'promised_date': forms.DateInput(attrs={'type': 'date'}),
            'style_notes': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class DepositForm(forms.Form):
    deposit_amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)


class CollectionForm(forms.Form):
    balance_payment = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
