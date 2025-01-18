from rest_framework import serializers
from .models import Bill, Return, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["barcode", "category", "sub_category", "size", "item_name"]

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ["full_name", "phone_number", "address"]

class ReturnSerializer(serializers.ModelSerializer):
    bill_number = BillSerializer()
    items = ItemSerializer(many=True)

    class Meta:
        model = Return
        fields = ["return_id", "bill_number", "items"]

    def create(self, validated_data):
        # Extract nested data
        bill_data = validated_data.pop("bill_number")
        items_data = validated_data.pop("items")
        
        # Create bill instance
        bill = Bill.objects.create(**bill_data)
        
        # Create return instance
        return_record = Return.objects.create(bill_number=bill, **validated_data)
        
        # Create item instances
        for item_data in items_data:
            Item.objects.create(return_record=return_record, **item_data)
        
        return return_record
