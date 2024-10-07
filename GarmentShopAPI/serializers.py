# serializers.py

from rest_framework import serializers
from .models import Company,Category

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'gst', 'pan', 'phone', 'email', 'address']
        
    def validate_gst(self, value):
        if len(value) != 15:
            raise serializers.ValidationError("GST number must be 15 characters long.")
        return value

    def validate_pan(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("PAN number must be 10 characters long.")
        return value


#Catagory Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'category_code', 'description']

    def validate_category_code(self, value):
        # Ensure category_code is unique
        if Category.objects.filter(category_code=value).exists():
            raise serializers.ValidationError("Category code must be unique.")
        return value

    def validate_category_name(self, value):
        # Ensure category_name is unique
        if Category.objects.filter(category_name=value).exists():
            raise serializers.ValidationError("Category name must be unique.")
        return value