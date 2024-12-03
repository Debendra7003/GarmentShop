from django.shortcuts import render
from .renderers import UserRenderer
from .serializers import UserRegisterSerializer,UserLoginSerializer,CompanySerializer,CategorySerializer,GetCategorySerializer,ItemSerializer,ItemCodeSerializer,TokenRefreshSerializer
from .serializers import DesignSerializer,DesignCreateUpdateSerializer,PartySerializer,TaxSerializer,FinancialYearSerializer,SubCategorySerializer
from rest_framework.response import Response
from rest_framework.views import APIView,View
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth import authenticate
from rest_framework import viewsets
from django.db.models import F
from .models import Company,Category,Item,Design,Party,Tax,FinancialYear,User,SubCategory,ItemSize




# Create your views here.
# ----------------------for token generation-----------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ---------------------------Registration view----------------------------
class UserRegisterView(APIView):
    # renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user= serializer.save()
            return Response({'msg' : "Register Successfull"},status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, user_name=None, format=None):
        # If 'user_name' is provided, fetch the specific user
        if user_name:
            user = User.objects.filter(user_name=user_name).first()
            if user:
                serializer = UserRegisterSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # If no 'user_name' is provided, fetch all users
        users = User.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, user_name=None, format=None):
        # If 'user_name' is provided, update the specific user
        if user_name:
            user = User.objects.filter(user_name=user_name).first()
            if user:
                # Perform update (allows updating any field, including 'user_name')
                serializer = UserRegisterSerializer(user, data=request.data, partial=True)  # Partial updates allowed
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # If no 'user_name' is provided, return an error message
        return Response({'error': 'Please provide a valid user_name for update'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_name=None, format=None):
        # If 'user_name' is provided, delete the specific user
        if user_name:
            user = User.objects.filter(user_name=user_name).first()
            if user:
                user.delete()  # Delete the user
                return Response({'msg': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # If no 'user_name' is provided, return an error message
        return Response({'error': 'Please provide a valid user_name for deletion'}, status=status.HTTP_400_BAD_REQUEST)
    
 
#---------------------------------Login View--------------------------------- 
class UserLoginView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer= UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_name=serializer.data.get('user_name')
            password=serializer.data.get('password')
            user = authenticate(user_name=user_name,password=password)
            if user is not None:
                response_data = {
                'user_name': user.user_name,
                'email': user.email,
                'fullname':user.fullname,
                'contact_number':user.contact_number,
                'role':user.role,
                'description':user.description,
                'is_admin': user.is_admin}
                token= get_tokens_for_user(user)
                return Response({'msg' : "Login Successfull",'user':response_data,'Token':token},status=status.HTTP_200_OK)
            else:
                return Response({'Errors' : {'non_fields_errors':['user_name or Password is not valid']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#--------------------- Get Access Tokemn using Refresh Token ------------------------------

class TokenRefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]
            try:
                refresh = RefreshToken(refresh_token)
                access_token = refresh.access_token
                return Response({"access_token": str(access_token)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Company view set
class CompanyViewSet(APIView):
    permission_classes=[IsAuthenticated]
    renderer_classes=[UserRenderer]
    def get(self, request, *args, **kwargs):
        """
        Retrieve company details by GST or get all companies.
        """
        gst = kwargs.get('gst', None)
        if gst is None:
            companies = Company.objects.all()
            serializer = CompanySerializer(companies, many=True)
            return Response({"message": "List of companies retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                company = Company.objects.get(gst=gst)
                serializer = CompanySerializer(company)
                return Response({"message": "Company details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Company.DoesNotExist:
                return Response({"message": "Company with this GST not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new company.
        """
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update company details using GST.
        """
        gst = kwargs.get('gst', None)
        try:
            company = Company.objects.get(gst=gst)
            serializer = CompanySerializer(company, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Company updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({"message": "Company with this GST not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        """
        Delete company using GST.
        """
        gst = kwargs.get('gst', None)
        try:
            company = Company.objects.get(gst=gst)
            company.delete()
            return Response({"message": "Company deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Company.DoesNotExist:
            return Response({"message": "Company with this GST not found."}, status=status.HTTP_404_NOT_FOUND)
#Catagory view set
class CategoryView(APIView):
    # def get(self, request, *args, **kwargs):
    #     # Retrieve all categories
    #     categories = Category.objects.all()  # Fetch all categories
    #     serializer = GetCategorySerializer(categories, many=True)  # Serialize the categories
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def get(self, request, category_name=None, *args, **kwargs):
    #     if category_name:
    #         try:
    #             # Retrieve the category based on category_name
    #             category = Category.objects.get(category_name=category_name)
    #             # Get all the subcategories related to this category
    #             subcategories = category.sub_category_name.all()
    #             # Serialize the subcategories using the SubCategorySerializer
    #             serializer = SubCategorySerializer(subcategories, many=True)
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         except Category.DoesNotExist:
    #             return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    #     return Response({"error": "Category name not provided"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, category_name=None, *args, **kwargs):
     if category_name:
        try:
            # Retrieve the category based on category_name
            category = Category.objects.get(category_name=category_name)
            # Serialize the category along with its subcategories
            data = {
                "category_code": category.category_code,
                "category_name": category.category_name,
                "description": category.description,
                "sub_category_name": [
                    {"name": subcategory.name} for subcategory in category.sub_category_name.all()
                ]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
     else:
        # Retrieve all categories along with their subcategories
        categories = Category.objects.prefetch_related('sub_category_name').all()
        data = []
        for category in categories:
            data.append({
                "category_code": category.category_code,
                "category_name": category.category_name,
                "description": category.description,
                "sub_category_name": [
                    {"name": subcategory.name} for subcategory in category.sub_category_name.all()
                ]
            })
        return Response(data, status=status.HTTP_200_OK)


    

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     serializer = CategorySerializer(data=data)
    #     if serializer.is_valid():
    #         category = serializer.save()  # `save()` now uses the corrected `create()` method
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
     data = request.data
    # Retrieve category_code and category_name from the request
     category_code = data.get('category_code')
     category_name = data.get('category_name')

     try:
        # Retrieve the existing category using category_code
        category = Category.objects.get(category_code=category_code)
        
        # Retrieve new subcategories from the request
        subcategories_data = data.get('sub_category_name', [])

        # Add the subcategories to the existing category
        for subcategory_dict in subcategories_data:
            subcategory_name = subcategory_dict.get('name')  # Extract the 'name' key
            if subcategory_name:  # Ensure the name is not empty
                subcategory, created = SubCategory.objects.get_or_create(name=subcategory_name)
                category.sub_category_name.add(subcategory)  # Add subcategory to ManyToMany field

        category.save()  # Save the updated category with new subcategories

        # Serialize the updated category
        serializer = CategorySerializer(category)

        # Return the updated category data
        return Response({
            "message": "Category added successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

     except Category.DoesNotExist:
        # If the category does not exist, create a new one along with subcategories
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            category = serializer.save()

            # Add new subcategories to the newly created category
            subcategories_data = data.get('sub_category_name', [])
            for subcategory_dict in subcategories_data:
                subcategory_name = subcategory_dict.get('name')  # Extract the 'name' key
                if subcategory_name:  # Ensure the name is not empty
                    subcategory, created = SubCategory.objects.get_or_create(name=subcategory_name)
                    category.sub_category_name.add(subcategory)

            category.save()  # Save the category with subcategories

            return Response({
                "message": "Category created successfully",
                "data": serializer.data}, 
                status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    def delete(self, request, category_name=None, *args, **kwargs):
        if category_name:
            try:
                # Retrieve the category by its name
                category = Category.objects.get(category_name=category_name)
                
                # Delete the category
                category.delete()
                
                return Response({
                    "message": f"Category '{category_name}' deleted successfully."
                }, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({
                    "error": f"Category '{category_name}' not found."
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "error": "Category name not provided."
            }, status=status.HTTP_400_BAD_REQUEST)
    
# Retrieve related subcategories for the given category    
class CategorySubCategoryView(APIView):
    def get(self, request, category_name, *args, **kwargs):
        try:
            # Retrieve the category by category_name
            category = Category.objects.get(category_name=category_name)

            # Retrieve related subcategories for the given category
            subcategories = category.sub_category_name.all()  # Using the Many-to-Many relationship

            # Serialize the subcategories
            serializer = SubCategorySerializer(subcategories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

# class CategoryViewSet(APIView):
#     permission_classes=[IsAuthenticated]
#     renderer_classes=[UserRenderer]
#     def get(self, request, category_code=None):
#         if category_code:
#             try:
#                 category = Category.objects.get(category_code=category_code)
#                 serializer = CategorySerializer(category)
#                 return Response({"data": serializer.data}, status=status.HTTP_200_OK)
#             except Category.DoesNotExist:
#                 return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             categories = Category.objects.all()
#             serializer = CategorySerializer(categories, many=True)
#             return Response({"data": serializer.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         # Check for existing category_name
#         if Category.objects.filter(category_name=request.data.get('category_name')).exists():
#             return Response({"category_name": ["Category with this name already exists."]}, 
#                             status=status.HTTP_400_BAD_REQUEST)
        
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Category created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, category_code):
#         try:
#             # Fetch the category based on category_code
#             category = Category.objects.get(category_code=category_code)

#             # Update the category with partial data without checking uniqueness of category_name or category_code
#             serializer = CategorySerializer(category, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "message": "Category updated successfully!",
#                     "data": serializer.data
#                 }, status=status.HTTP_200_OK)
            
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         except Category.DoesNotExist:
#             return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
#Item view set
class ItemViewSet(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    def get(self, request, item_code=None):
        """
        Retrieve a list of all items or a specific item by item_code.
        - If 'item_code' is provided, return the details of the specified item.
        - If 'item_code' is not provided, return a list of all items.
        """
        if item_code is None:
            items = Item.objects.all()  # Get all items
            serializer = ItemSerializer(items, many=True)  # Serialize the data
            return Response({
                "message": "List of items retrieved successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            try:
                item = Item.objects.get(item_code=item_code)  # Get the specific item by item_code
                serializer = ItemSerializer(item)  # Serialize the item data
                return Response({
                    "message": "Item details retrieved successfully!",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                return Response({
                    "message": "Item not found."
                }, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request):
    #     """
    #     Create a new item.
    #     """
    #     serializer = ItemSerializer(data=request.data)  # Create a serializer with request data
    #     if serializer.is_valid():  # Validate the serializer
    #         serializer.save()  # Save the new item
    #         return Response({
    #             "message": "Item created successfully!",
    #             "data": serializer.data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response({
    #         "message": "Item creation failed.",
    #         "errors": serializer.errors
    #     }, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors

    def post(self, request):
        """
        Create a new item or update stock_quantity for an existing item_code.
        """
        item_code = request.data.get('item_code')

        # Check if the item_code is provided in the request data
        if not item_code:
            return Response({
                "message": "Item code is required for updating or creating the item."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the item already exists
        item = Item.objects.filter(item_code=item_code).first()

        # If the item exists, update stock quantities for sizes
        if item:
            sizes_data = request.data.get('sizes', [])
            
            # Iterate through the sizes passed in the request
            for size_data in sizes_data:
                size_instance = ItemSize.objects.filter(item=item, size=size_data['size']).first()

                if size_instance:
                    # If size exists, update the stock_quantity by adding the new value to the existing one
                    size_instance.stock_quantity = F('stock_quantity') + size_data['stock_quantity']
                    size_instance.save()
                else:
                    # If size does not exist, create a new size entry
                    ItemSize.objects.create(
                        item=item,
                        size=size_data['size'],
                        stock_quantity=size_data['stock_quantity']
                    )

            # Return the updated item with its sizes
            return Response({
                "message": "Stock quantities updated successfully!",
                "data": ItemSerializer(item).data  # Return the updated item details
            }, status=status.HTTP_200_OK)

        else:
            # If the item does not exist, create a new item
            serializer = ItemSerializer(data=request.data)  # Create a new item serializer with request data
            if serializer.is_valid():  # Validate the serializer
                item = serializer.save()  # Save the new item
                # Return the new item data after creation
                return Response({
                    "message": "Item created successfully!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors if the serializer is invalid
            return Response({
                "message": "Item creation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    
    
    def put(self, request, item_code):
        """
        Update an existing item by item_code.
        Allow updating individual fields.
        """
        try:
            item = Item.objects.get(item_code=item_code)  # Get the specific item by item_code
            serializer = ItemSerializer(item, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():  # Validate the serializer
                serializer.save()  # Save the updated item
                return Response({
                    "message": "Item updated successfully!",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Item update failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors
        except Item.DoesNotExist:
            return Response({
                "message": "Item not found."
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, item_code):
        """
        Delete an item by item_code.
        """
        try:
            item = Item.objects.get(item_code=item_code)  # Get the specific item by item_code
            item.delete()  # Delete the item
            return Response({
                "message": "Item deleted successfully!"
            }, status=status.HTTP_204_NO_CONTENT)  # Return 204 No Content
        except Item.DoesNotExist:
            return Response({
                "message": "Item not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
#ItemCode view set
class ItemCodeViewSet(APIView):
    permission_classes=[IsAuthenticated]
    renderer_classes=[UserRenderer]
    """
    API to retrieve only 'id', 'item_name', and 'item_code'.
    Uses ItemCodeSerializer.
    """

    def get(self, request, pk=None):
        if pk is None:
            items = Item.objects.all()  # Get all items
            serializer = ItemCodeSerializer(items, many=True)  # Serialize with limited fields
            return Response({"message": "List of items retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                item = Item.objects.get(pk=pk)
                serializer = ItemCodeSerializer(item)  # Serialize with limited fields
                return Response({"message": "Item details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
#Design view set
            
class DesignViewSet(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, design_code=None):
        """
        Retrieve all designs or a specific design by design_code.
        """
        if design_code is None:
            designs = Design.objects.all()
            serializer = DesignSerializer(designs, many=True)
            return Response({"message": "Design list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                design = Design.objects.get(design_code=design_code)
                serializer = DesignSerializer(design)
                return Response({"message": "Design details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Design.DoesNotExist:
                return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new design.
        """
        serializer = DesignCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Design created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, design_code):
        """
        Update an existing design by design_code.
        """
        try:
            design = Design.objects.get(design_code=design_code)
            serializer = DesignCreateUpdateSerializer(design, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Design updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Design.DoesNotExist:
            return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, design_code):
        """
        Delete a design by design_code.
        """
        try:
            design = Design.objects.get(design_code=design_code)
            design.delete()
            return Response({"message": "Design deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Design.DoesNotExist:
            return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)

#Party view set
class PartyViewSet(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, party_name=None):
        """
        Retrieve all parties or a specific party by party_name.
        """
        if party_name is None:
            parties = Party.objects.all()
            serializer = PartySerializer(parties, many=True)
            return Response({"message": "Party list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                party = Party.objects.get(party_name=party_name)
                serializer = PartySerializer(party)
                return Response({"message": "Party details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Party.DoesNotExist:
                return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new party.
        """
        serializer = PartySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Party created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, party_name):
        """
        Update an existing party by party_name.
        """
        try:
            party = Party.objects.get(party_name=party_name)
            serializer = PartySerializer(party, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Party updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Party.DoesNotExist:
            return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, party_name):
        """
        Delete a party by party_name.
        """
        try:
            party = Party.objects.get(party_name=party_name)
            party.delete()
            return Response({"message": "Party deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Party.DoesNotExist:
            return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

#Tax view set
class TaxViewSet(APIView):
    permission_classes=[IsAuthenticated]
    renderer_classes=[UserRenderer]
    def get(self, request, pk=None):
        if pk:
            try:
                tax = Tax.objects.get(pk=pk)
                serializer = TaxSerializer(tax)
                return Response({"message": "Tax details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Tax.DoesNotExist:
                return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            taxes = Tax.objects.all()
            serializer = TaxSerializer(taxes, many=True)
            return Response({"message": "Tax list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaxSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tax created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            tax = Tax.objects.get(pk=pk)
            serializer = TaxSerializer(tax, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Tax updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tax.DoesNotExist:
            return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            tax = Tax.objects.get(pk=pk)
            tax.delete()
            return Response({"message": "Tax deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Tax.DoesNotExist:
            return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)
#Financial Year view
class FinancialYearViewSet(APIView):
    permission_classes=[IsAuthenticated]
    renderer_classes=[UserRenderer]

    def get(self, request, pk=None):
        """
        Retrieve all financial years or a specific one by ID.
        """
        if pk is None:
            financial_years = FinancialYear.objects.all()
            serializer = FinancialYearSerializer(financial_years, many=True)
            return Response({"message": "Financial year list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                financial_year = FinancialYear.objects.get(pk=pk)
                serializer = FinancialYearSerializer(financial_year)
                return Response({"message": "Financial year details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except FinancialYear.DoesNotExist:
                return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new financial year.
        """
        serializer = FinancialYearSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Financial year created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing financial year.
        """
        try:
            financial_year = FinancialYear.objects.get(pk=pk)
            serializer = FinancialYearSerializer(financial_year, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Financial year updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FinancialYear.DoesNotExist:
            return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a financial year.
        """
        try:
            financial_year = FinancialYear.objects.get(pk=pk)
            financial_year.delete()
            return Response({"message": "Financial year deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except FinancialYear.DoesNotExist:
            return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)