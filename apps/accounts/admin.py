from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'


class UserAdmin(BaseUserAdmin):
    inlines = [StaffProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'business_unit', 'is_active']
    list_filter = ['role', 'business_unit', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
