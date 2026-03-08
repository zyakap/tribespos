from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import LoginForm, PINLoginForm
from .models import StaffProfile
from apps.core.mixins import RoleRequiredMixin


def login_view(request):
    if request.user.is_authenticated:
        return redirect('reporting:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'reporting:dashboard'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def pin_login_view(request):
    """Quick PIN login for POS terminals."""
    if request.method == 'POST':
        pin = request.POST.get('pin', '')
        try:
            profile = StaffProfile.objects.get(pin=pin, is_active=True)
            login(request, profile.user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({'success': True, 'redirect': '/pos/'})
        except StaffProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid PIN'}, status=400)
    return render(request, 'accounts/pin_login.html')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'profile': request.user.staff_profile})
