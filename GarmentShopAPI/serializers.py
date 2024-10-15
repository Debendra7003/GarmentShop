from rest_framework import serializers
from .models import User,Company,Category,Item,Design,Party,Tax,FinancialYear


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


#Catagory Creation Serializer
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

#Retrive Catagory_code and catagory_name
class CategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_code', 'category_name']

#Item Serializer
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'item_code', 'category', 'hsn_code', 'unit_price', 'stock_quantity', 'description']

    def validate_item_code(self, value):
        # Ensure item_code is unique
        if Item.objects.filter(item_code=value).exists():
            raise serializers.ValidationError("Item code must be unique.")
        return value
#Item Report
class ItemReportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.catagory_name', read_only=True)
    profit_margin = serializers.FloatField(read_only=True)  # Computed in the model as a property

    class Meta:
        model = Item
        fields = ['item_name', 'total_quantity_sold', 'total_sales_amount', 'category_name', 'profit_margin']
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
#Party Serializer
class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'party_name', 'party_type', 'phone', 'email', 'address', 'registration_number', 'gst_number', 'description']
#Tax Serializer
class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id', 'tax_name', 'tax_percentage', 'description']
#Financial Year Serializer
class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = ['id', 'financial_year_name', 'start_date', 'end_date', 'status', 'description']