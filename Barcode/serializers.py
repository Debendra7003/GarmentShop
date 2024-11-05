# barcode_app/serializers.py
from rest_framework import serializers
from .models import BarcodeItem

class BarcodeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeItem
        fields = ['item_name', 'description', 'size', 'mrp']
