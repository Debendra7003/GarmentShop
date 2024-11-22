from rest_framework import serializers
from .models import ItemInformation,PricingAndTax,PaymentAndNarration,PartyInformation

class ItemInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemInformation
        fields = ['barcodenumber', 'itemname', 'unit', 'unitprice', 'total_item_price']

class PricingAndTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingAndTax
        fields = ['tax', 'discount', 'grand_total', 'total_price']

class PaymentAndNarrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAndNarration
        fields = ['payment_method1', 'payment_method2', 'payment_amount1', 'payment_amount2']

class PartyInformationSerializer(serializers.ModelSerializer):
    items = ItemInformationSerializer(many=True)
    pricing_tax = PricingAndTaxSerializer()
    payment_narration = PaymentAndNarrationSerializer()

    class Meta:
        model = PartyInformation
        fields = ['invoicenumber','partyname', 'mobilenumber', 'address', 'gstnumber', 'items', 'pricing_tax', 'payment_narration']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        pricing_tax_data = validated_data.pop('pricing_tax')
        payment_narration_data = validated_data.pop('payment_narration')

        # Create Party
        party = PartyInformation.objects.create(**validated_data)

        # Calculate total item price and grand total
        grand_total = 0
        for item_data in items_data:
            unit = item_data['unit']
            unitprice = item_data['unitprice']
            total_item_price = unit * unitprice
            item_data['total_item_price'] = total_item_price
            grand_total += total_item_price
            ItemInformation.objects.create(party=party, **item_data)

        # Apply tax and discount
        tax_percentage = pricing_tax_data['tax']
        discount_percentage = pricing_tax_data['discount']
        total_price = grand_total + (grand_total * tax_percentage / 100) - (grand_total * discount_percentage / 100)

        # Save pricing and tax
        pricing_tax_data['grand_total'] = grand_total
        pricing_tax_data['total_price'] = total_price
        PricingAndTax.objects.create(party=party, **pricing_tax_data)

        # Save payment and narration
        PaymentAndNarration.objects.create(party=party, **payment_narration_data)

        return party
