# barcode_app/serializers.py
from rest_framework import serializers
from .models import BarcodeItem,BarcodeGen

class BarcodeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeItem
        fields = ['item_name', 'description', 'size', 'mrp']


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeGen
        fields = ['shop_name', 'item_name', 'item_size', 'item_price', 'serial_number', 'barcode_image']
        read_only_fields = ['serial_number', 'barcode_image']


    # def validate_shop_name(self, value):
    #     # Check the length of serial_number
    #     if len(value) > 25:
    #         raise serializers.ValidationError("Shop name cannot exceed 25 characters.")
    #     return value
    
class BarcodeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeGen
        # Exclude the barcode_image field
        fields = ['shop_name', 'item_name', 'item_size', 'item_price', 'serial_number']