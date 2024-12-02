from rest_framework import serializers
from .models import User,Company,Category,SubCategory,Item,Design,Party,Tax,FinancialYear,ItemSize

""" ------------User registration serializers--------------"""
class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model= User
        fields=['user_name','password','password2','fullname', 'email', 'contact_number', 'role','description']

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
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    sub_category_name = SubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['category_code', 'category_name', 'description', 'sub_category_name']

    def create(self, validated_data):
        sub_category_data = validated_data.pop('sub_category_name')
        category = Category.objects.create(**validated_data)
        
        for sub_cat in sub_category_data:
            sub_category, created = SubCategory.objects.get_or_create(name=sub_cat['name'])
            category.sub_category_name.add(sub_category)

        return category
    
class GetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_code', 'category_name']
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'category_name', 'category_code', 'description']

#     def validate_category_code(self, value):
#         # Ensure category_code is unique
#         if Category.objects.filter(category_code=value).exists():
#             raise serializers.ValidationError("Category code must be unique.")
#         return value

#     def validate_category_name(self, value):
#         # Ensure category_name is unique
#         if Category.objects.filter(category_name=value).exists():
#             raise serializers.ValidationError("Category name must be unique.")
#         return value
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['category_name', 'category_code', 'description']
#     def validate(self, data):
#         # Get the instance if it's an update operation
#         instance = self.instance
#         # Check uniqueness for category_name only if it’s changed
#         if 'category_name' in data and instance and data['category_name'] != instance.category_name:
#             if Category.objects.filter(category_name=data['category_name']).exclude(pk=instance.pk).exists():
#                 raise serializers.ValidationError({"category_name": "Category name must be unique."})
#         # Check uniqueness for category_code only if it’s changed
#         if 'category_code' in data and instance and data['category_code'] != instance.category_code:
#             if Category.objects.filter(category_code=data['category_code']).exclude(pk=instance.pk).exists():
#                 raise serializers.ValidationError({"category_code": "Category code must be unique."})
#         return data
#Retrive Catagory_code and catagory_name
class CategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_code', 'category_name']

#ItemSize Serializers

class ItemSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemSize
        fields = ['size', 'stock_quantity','unit_price']

#Item Serializer
class ItemSerializer(serializers.ModelSerializer):
    sizes = ItemSizeSerializer(many=True)

    class Meta:
        model = Item
        fields = [
            'id', 'item_name', 'item_code', 'category_item', 'sub_category',
            'hsn_code', 'description', 'created_at', 'sizes'
        ]

    def validate_item_code(self, value):
        """
        Ensure `item_code` is unique only for new instances.
        """
        if not self.instance:  # If instance is None, it's a creation request
            if Item.objects.filter(item_code=value).exists():
                raise serializers.ValidationError("Item code must be unique.")
        return value

    def create(self, validated_data):
        """
        Create a new Item and associated ItemSize objects.
        """
        sizes_data = validated_data.pop('sizes', [])
        item = Item.objects.create(**validated_data)
        for size_data in sizes_data:
            ItemSize.objects.create(item=item, **size_data)
        return item

    def update(self, instance, validated_data):
        """
        Update an Item and associated ItemSize objects.
        """
        sizes_data = validated_data.pop('sizes', None)

        # Update main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested sizes
        if sizes_data:
            # Existing sizes keyed by size field
            existing_sizes = {size.size: size for size in instance.sizes.all()}
            new_sizes = {size_data['size']: size_data for size_data in sizes_data}

            # Update or create sizes
            for size, size_data in new_sizes.items():
                if size in existing_sizes:
                    size_obj = existing_sizes[size]
                    for attr, value in size_data.items():
                        setattr(size_obj, attr, value)
                    size_obj.save()
                else:
                    ItemSize.objects.create(item=instance, **size_data)

            # Remove sizes not included in the new data
            for size in set(existing_sizes.keys()) - set(new_sizes.keys()):
                existing_sizes[size].delete()

        return instance
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
    associated_items = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    class Meta:
        model = Design
        fields = ['design_name', 'design_code', 'description', 'associated_items']


class DesignCreateUpdateSerializer(serializers.ModelSerializer):
    associated_items = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    class Meta:
        model = Design
        fields = ['design_name', 'design_code', 'description', 'associated_items']
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