from django.db import models
from django.contrib.auth.models import User
from apps.core.models import SoftDeleteModel, BusinessUnit


class StaffProfile(SoftDeleteModel):
    ROLES = [
        ('superadmin', 'Super Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('waiter', 'Waiter'),
        ('barista', 'Barista'),
        ('tailor', 'Tailor'),
        ('warehouse', 'Warehouse'),
        ('accountant', 'Accountant'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    business_unit = models.ForeignKey(
        BusinessUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff'
    )
    role = models.CharField(max_length=20, choices=ROLES)
    pin = models.CharField(max_length=6, blank=True, help_text='Quick PIN for POS login')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
