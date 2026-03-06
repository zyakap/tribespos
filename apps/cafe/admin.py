from django.contrib import admin
from .models import ModifierGroup, Modifier, ProductModifierGroup


class ModifierInline(admin.TabularInline):
    model = Modifier
    extra = 1


@admin.register(ModifierGroup)
class ModifierGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_unit', 'required', 'min_selections', 'max_selections']
    inlines = [ModifierInline]
