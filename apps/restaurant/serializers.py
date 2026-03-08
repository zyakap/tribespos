from rest_framework import serializers
from .models import RestaurantTable, KitchenTicket, KitchenTicketLine


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = '__all__'


class KitchenTicketLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenTicketLine
        fields = '__all__'


class KitchenTicketSerializer(serializers.ModelSerializer):
    lines = KitchenTicketLineSerializer(many=True, read_only=True)

    class Meta:
        model = KitchenTicket
        fields = '__all__'
