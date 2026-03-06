from rest_framework import serializers
from .models import Account, JournalEntry, JournalLine, ARInvoice, TaxRate


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class JournalLineSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = JournalLine
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = '__all__'
