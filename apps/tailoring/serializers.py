from rest_framework import serializers
from .models import TailoringOrder, TailoringStageLog


class TailoringStageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailoringStageLog
        fields = '__all__'


class TailoringOrderSerializer(serializers.ModelSerializer):
    stage_logs = TailoringStageLogSerializer(many=True, read_only=True)

    class Meta:
        model = TailoringOrder
        fields = '__all__'
