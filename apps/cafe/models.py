from django.db import models
from apps.core.models import TimeStampedModel, BusinessUnit
from apps.products.models import Product


class ModifierGroup(TimeStampedModel):
    name = models.CharField(max_length=100)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name='modifier_groups')
    required = models.BooleanField(default=False)
    min_selections = models.IntegerField(default=0)
    max_selections = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Modifier(models.Model):
    group = models.ForeignKey(ModifierGroup, on_delete=models.CASCADE, related_name='modifiers')
    name = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.group.name}: {self.name}"


class ProductModifierGroup(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='modifier_groups')
    modifier_group = models.ForeignKey(ModifierGroup, on_delete=models.CASCADE)

    class Meta:
        unique_together = [('product', 'modifier_group')]
