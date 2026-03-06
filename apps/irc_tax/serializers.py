from rest_framework import serializers
from .models import GSTReturn, SWTRemittance, CITReturn, ProvisionalTaxInstalment


class GSTReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSTReturn
        fields = '__all__'


class SWTRemittanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SWTRemittance
        fields = '__all__'


class CITReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = CITReturn
        fields = '__all__'
