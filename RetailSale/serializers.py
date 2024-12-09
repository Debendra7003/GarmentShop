from rest_framework import serializers
from .models import Order, Item
from decimal import Decimal

class ItemSerializer(serializers.ModelSerializer):
    total_item_price = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ['id', 'barcode','category','sub_category','size', 'item_name', 'unit', 'unit_price', 'total_item_price']

class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)
    grand_total = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'fullname', 'phone_number', 'address', 'tax', 'discount', 
                  'grand_total', 'total_price', 'payment_method1', 'payment_method2', 
                  'narration', 'payment_method1_amount', 'payment_method2_amount','saletype', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])  # Extract the items data
        order = Order.objects.create(**validated_data)  # Create the Order instance

        # Create Item instances and add them to the order
        for item_data in items_data:
            item = Item.objects.create(order=order, **item_data)
            order.items.add(item)  # Add the item to the order's items

        # Calculate total price and grand total after items are added
        order.total_price = order.calculate_total_price()
        order.grand_total = order.calculate_grand_total()
        order.save()  # Save the order with updated prices

        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Handle Decimal fields explicitly to make them JSON serializable
        for field in ['grand_total', 'total_price', 'tax', 'discount']:
            value = representation.get(field)
            if isinstance(value, Decimal):
                # Convert Decimal to string to avoid JSON serialization error
                representation[field] = str(value)  # Or you can use float(value) if you prefer a float

        return representation
