from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = ['id', 'role', 'business_unit', 'is_active']


class UserSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'staff_profile']


class HarhurumTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        if hasattr(user, 'staff_profile'):
            token['role'] = user.staff_profile.role
            token['business_unit'] = user.staff_profile.business_unit_id
        return token
