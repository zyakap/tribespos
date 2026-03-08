from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['code', 'name', 'contact_person', 'phone', 'email', 'address', 'payment_terms', 'currency', 'tax_number']
