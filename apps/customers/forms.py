from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'customer_type', 'credit_limit']
        widgets = {cls: forms.TextInput(attrs={'class': 'form-control'}) for cls in ['name', 'phone', 'email']}
