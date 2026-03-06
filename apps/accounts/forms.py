from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import StaffProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class PINLoginForm(forms.Form):
    pin = forms.CharField(
        max_length=6, min_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN', 'autocomplete': 'off'})
    )


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['business_unit', 'role', 'pin']
        widgets = {
            'pin': forms.PasswordInput(attrs={'autocomplete': 'off'}),
        }
