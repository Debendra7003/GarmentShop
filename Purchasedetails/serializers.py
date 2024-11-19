from rest_framework import serializers
from .models import PurchaseEntry

class PurchaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseEntry
        fields = '__all__'
        read_only_fields = ('reference_voucher_number', 'discount_amount', 'taxable_amount', 'gst_amount', 'purchase_amount')
