<<<<<<< HEAD
# serializers.py

from rest_framework import serializers
from .models import Company,Category

=======
from rest_framework import serializers
from .models import User,Company,Catagory,Item,Design


""" ------------User registration serializers--------------"""
class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model= User
        fields=['user_name','password','password2']

        extra_kwargs={
            'password':{'write_only':True}
        }

    #-------------------validate password & Confirm Password -----------------
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm password doesn't match.")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    # super().create(validated_data)


""" ---------------User Login serializers-------------"""
class UserLoginSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=100)
    class Meta:
        model=User
        fields=['user_name','password']

""" ---------------User profile serializers to get all the data about User-------------"""

class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

#Company Serializer
>>>>>>> 41f2a9330573d80436a6055c951abcd1418c0c58
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


<<<<<<< HEAD
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
=======
#Catagory Creation Serializer
class CatagorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Catagory
        fields = ['id', 'catagory_name', 'catagory_code', 'description']

    def validate_category_code(self, value):
        # Ensure category_code is unique
        if Catagory.objects.filter(category_code=value).exists():
            raise serializers.ValidationError("Category code must be unique.")
        return value

    def validate_catagory_name(self, value):
        # Ensure category_name is unique
        if Catagory.objects.filter(catagory_name=value).exists():
            raise serializers.ValidationError("Category name must be unique.")
        return value

#Retrive Catagory_code and catagory_name
class CatagoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catagory
        fields = ['catagory_code', 'catagory_name']

#Item Serializer
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'item_code', 'catagory', 'hsn_code', 'unit_price', 'stock_quantity', 'description']

    def validate_item_code(self, value):
        # Ensure item_code is unique
        if Item.objects.filter(item_code=value).exists():
            raise serializers.ValidationError("Item code must be unique.")
        return value
    
class ItemCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Item
        fields=['id','item_name','item_code']
class DesignSerializer(serializers.ModelSerializer):
    associated_items = ItemCodeSerializer(many=True, read_only=True)  # Display item names

    class Meta:
        model = Design
        fields = ['id', 'design_name', 'design_code', 'description', 'associated_items']

class DesignCreateUpdateSerializer(serializers.ModelSerializer):
    # Allows you to pass item IDs to associate items with a design
    associated_items = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), many=True)

    class Meta:
        model = Design
        fields = ['id', 'design_name', 'design_code', 'description', 'associated_items']
>>>>>>> 41f2a9330573d80436a6055c951abcd1418c0c58
